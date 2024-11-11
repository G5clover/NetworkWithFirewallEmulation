from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.log import setLogLevel
from mininet.cli import CLI

class MyTopo(Topo):
    "Simple topology example."

    def build(self):
        "Create custom topo."

        # Add hosts and central switch
        hosts = {}
        for i in range(1, 7):
            hosts[i] = self.addHost('h{}'.format(i))
        s1 = self.addSwitch('s1')

        # Add links
        for i in hosts:
            self.addLink(s1, hosts[i])

        h8 = self.addHost('h8', ip='10.0.0.8')
        self.addLink(s1, h8)

# Create an instance of the topology
topos = {'mytopo': (lambda: MyTopo())}

if __name__ == '__main__':
    setLogLevel('info')
    net = Mininet(topo=MyTopo(), controller=None)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    # Add NAT node to provide external network access for hosts
    nat = net.addNAT().configDefault()
    net.start()
    # Set DNS for all hosts
    for host in net.hosts:
        host.cmd('cp /etc/resolv.conf /tmp/resolv.conf')
        host.cmd('echo nameserver 8.8.8.8 >> /tmp/resolv.conf')
        host.cmd('mv /tmp/resolv.conf /etc/resolv.conf')
    CLI(net)
    net.stop()
