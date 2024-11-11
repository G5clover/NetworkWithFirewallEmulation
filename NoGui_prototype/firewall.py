from pox.core import core
import pox.openflow.libopenflow_01 as of
import socket
import json
import threading

# A set of ports to block
blocked_ports = []

# Packets to block based on IP source and destination
# format example: [('10.0.0.3', '10.0.0.4'), ('10.0.0.2', '8.8.8.8')]
ips_table = []

# A dictionary to keep track of all connections
# format example: {(src_ip, src_port, dst_ip, dst_port): state}
tcp_connections = {}

# IPs of connnected hosts in the network
ip_in_net = {
    '10.0.0.1',
    '10.0.0.2',
    '10.0.0.3',
    '10.0.0.4',
    '10.0.0.5',
    '10.0.0.6',
}

def block_handler(event):
    tcpp = event.parsed.find('tcp')
    ipp = event.parsed.find('ipv4')

    # Block from IP rules
    if ipp:
        for rule in ips_table:
            rule_src_ip, rule_dst_ip = rule
            # If the destination ip is * then the source ip is blocked to all destinations
            if (rule_src_ip == '*' or str(ipp.srcip) == rule_src_ip) and (rule_dst_ip == '*' or str(ipp.dstip) == rule_dst_ip):
                core.getLogger("blocker").debug("Blocked IP packet %s <-> %s",
                                                ipp.srcip, ipp.dstip)
                event.halt = True
                return

    if not tcpp:
        return

    # Bllock from port blacklist
    if str(tcpp.srcport) in blocked_ports or str(tcpp.dstport) in blocked_ports:
        core.getLogger("blocker").debug("Blocked TCP from port rule %s <-> %s",
                                        tcpp.srcport, tcpp.dstport)
        event.halt = True
        return

    # Block new TCP connection requests from outside the network
    if ipp and tcpp.SYN and not tcpp.ACK:
        try:
            if str(ipp.srcip) not in ip_in_net:
                core.getLogger("blocker").debug("Blocked new TCP connection request from %s <-> %s",
                                                ipp.srcip, ipp.dstip)
                event.halt = True
            else:
                tcp_connections[(str(ipp.srcip), tcpp.srcport, str(ipp.dstip), tcpp.dstport)] = 'ESTABLISHED'
                core.getLogger("blocker").debug("New connection made from %s:%s to %s:%s",
                                                  ipp.srcip, tcpp.srcport, ipp.dstip, tcpp.dstport)
        except AttributeError:
            core.getLogger("blocker").error("Error accessing IP attributes")

    # Allow packets transfer from already establlished connections
    if (str(ipp.srcip), tcpp.srcport, str(ipp.dstip), tcpp.dstport) in tcp_connections:
        core.getLogger("blocker").debug("Allowing existing connection packet from %s:%s to %s:%s",
                                          ipp.srcip, tcpp.srcport, ipp.dstip, tcpp.dstport)
        core.getLogger("blocker").error(tcp_connections)
        return

    # Remove connection when TCP end connextion flag sent
    if tcpp.FIN:
        key = (str(ipp.dstip), tcpp.dstport, str(ipp.srcip), tcpp.srcport)
        if key in tcp_connections:
            del tcp_connections[key]
            core.getLogger("blocker").debug("TCP Connection ended: %s", key)



def unblock_port(ports):
    for port in ports:
        if port in blocked_ports:
            blocked_ports.remove(port)
        else:
            core.getLogger("blocker").info(f"{port} already unblocked")
    core.getLogger("blocker").info(f"Unblocked ports: {ports}")

def block_port(ports):
    for port in ports:
        if port not in blocked_ports:
            blocked_ports.append(port)
        else:
            core.getLogger("blocker").info(f"{port} already blocked")
    core.getLogger("blocker").info(f"Blocked ports: {ports}")

def add_ip_rule(src_ip, dst_ip):
    rule = (src_ip, dst_ip)
    if rule not in ips_table:
        ips_table.append(rule)
        core.getLogger("blocker").info(f"Added IP rule: {src_ip} -> {dst_ip}")
    else:
        core.getLogger("blocker").info(f"IP rule already exists: {src_ip} -> {dst_ip}")

def remove_ip_rule(src_ip, dst_ip):
    rule = (src_ip, dst_ip)
    if rule in ips_table:
        ips_table.remove(rule)
        core.getLogger("blocker").info(f"Removed IP rule: {src_ip} -> {dst_ip}")
    else:
        core.getLogger("blocker").info(f"IP rule not found: {src_ip} -> {dst_ip}")

def start_tcp_server():
    # Start a TCP server to listen for JSON messages
    port = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))  # Bind to all interfaces on port 5000
    server_socket.listen(5)
    core.getLogger("blocker").info(f"TCP server started, listening for messages from client at port {port}...")

    while True:
        client_socket, addr = server_socket.accept()
        core.getLogger("blocker").info(f"Connection from {addr}")
        handle_client(client_socket)

def handle_client(client_socket):
    # Handle incoming client connections
    with client_socket:
        data = client_socket.recv(1024).decode('utf-8')
        try:
            msg = json.loads(data)
            protocol = msg.get('protocol')
            action = msg.get('action')

            if protocol == 'ipv4':
                src_ip = msg.get('src_ip')
                dst_ip = msg.get('dst_ip')
                if action == 'add' and src_ip and dst_ip:
                    add_ip_rule(src_ip, dst_ip)
                elif action == 'remove' and src_ip and dst_ip:
                    remove_ip_rule(src_ip, dst_ip)

            elif protocol == 'tcp':
                ports = msg.get('ports') #TODO fix port blocking logic
                if action == 'add':
                    block_port(ports)
                elif action == 'remove':
                    unblock_port(ports)
                    
        except json.JSONDecodeError:
            core.getLogger("blocker").error("Received invalid JSON")
        except Exception as e:
            core.getLogger("blocker").error(f"Error processing client request: {e}")

def launch():
    # Listen to packet events
    core.openflow.addListenerByName("PacketIn", block_handler)

    # Start the TCP server in a separate thread
    threading.Thread(target=start_tcp_server, daemon=True).start()

    core.getLogger("blocker").info("Firewall initialized and TCP server started.")

