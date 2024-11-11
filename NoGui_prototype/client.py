import socket
import json

def firewall_ip_rule_message(protocol, action, src_ip=None, dst_ip=None, ports=None):
    if protocol == 'ipv4':
        message = {
            'protocol': protocol,
            'action': action,
            'src_ip': src_ip,
            'dst_ip': dst_ip
        }
    elif protocol == 'tcp':
        message = {
            'protocol': protocol,
            'action': action,
            'ports': ports
        }


    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            # Connect to firewall
            client_socket.connect(('127.0.0.1', 5000))
            client_socket.sendall(json.dumps(message).encode('utf-8'))
            print("Updated firewall rule", message)
        except ConnectionRefusedError:
            print("Connection failed")

def main():
    client_title = '''

 _____ _                        _ _   __  __                                    
|  ___(_)_ __ _____      ____ _| | | |  \/  | __ _ _ __   __ _  __ _  ___ _ __  
| |_  | | '__/ _ \ \ /\ / / _` | | | | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__| 
|  _| | | | |  __/\ V  V / (_| | | | | |  | | (_| | | | | (_| | (_| |  __/ |    
|_|   |_|_|  \___| \_/\_/ \__,_|_|_| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|    
                                                               |___/            

'''
    print(client_title)
    while True:
        print("1. Add IP Rule")
        print("2. Remove IP Rule")
        print("3. Block ports")
        print("4. Unblock ports")
        print("5. Exit")
        print()

        option = input("Choose an option: ")

        if option == '1':
            src_ip = input("Enter source ipv4 (or * for all source): ")
            dst_ip = input("Enter destination  ipv4 (or * for all destinations): ")
            firewall_ip_rule_message('ipv4', 'add', src_ip, dst_ip)

        elif option == '2':
            src_ip = input("Enter source ipv4 (or * for any): ")
            dst_ip = input("Enter destination ipv4 (or * for any): ")
            firewall_ip_rule_message('ipv4', 'remove', src_ip, dst_ip)

        elif option == '3':
            ports = list(map(str.strip, input("Enter the ports to block (port1, port2, port3, ...): ").split(',')))
            firewall_ip_rule_message('tcp', 'add', None, None, ports)

        elif option == '4':
            ports = list(map(str.strip, input("Enter the ports to unblock  (port1, port2, port3, ...): ").split(',')))
            firewall_ip_rule_message('tcp', 'remove', None, None, ports)

        elif option == '5':
            print("Closing client")
            break

        else:
            print("Please choose one of the listed options")

        print()
if __name__ == "__main__":
    main()

