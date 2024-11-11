from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI

class MyTopo(Topo):
    "Simple topology example."

    def build(self):
        "Create custom topo."

        # Add hosts and central switch
        hosts = {}
        for i in range(1, 7):
            hosts[i] = self.addHost(f'h{i}')
        s1 = self.addSwitch('s1')

        # Add links
        for i in hosts:
            self.addLink(s1, hosts[i])

# Create an instance of the topology
topos = {'mytopo': (lambda: MyTopo())}

if __name__ == '__main__':
    net = Mininet(topo=MyTopo(), controller=RemoteController)
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    net.start()
    CLI(net)
    net.stop()
                  

