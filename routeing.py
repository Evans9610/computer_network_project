from mininet.cli import CLI
from mininet.net import Mininet
from mininet.link import Link,TCLink,Intf
from mininet.node import OVSKernelSwitch, RemoteController

if '__main__' == __name__:
    net = Mininet(link=TCLink)
    h1 = net.addHost('h1')
    h11 = net.addHost('h11')
    s1 = net.addSwitch('s1')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    r1 = net.addHost('r1')
    r2 = net.addHost('r2')
    r3 = net.addHost('r3')

    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)

    net.addLink(h1, s1)
    net.addLink(h11,s1)
    net.addLink(s1, r1)
    net.addLink(h2, r2)
    net.addLink(r1, r2)

    net.build()
    c0.start()
    s1.start([c0])

    r1.cmd('ifconfig r1-eth0 0')
    r1.cmd('ifconfig r1-eth1 0')
    r1.cmd('ifconfig r1-eth0 192.168.10.254 netmask 255.255.255.0')
    r1.cmd('ifconfig r1-eth1 192.168.40.1 netmask 255.255.255.0')
    r1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    r1.cmd('ip route add 192.168.20.0/24 via 192.168.40.2')
    r2.cmd('ifconfig r2-eth0 0')
    r2.cmd('ifconfig r2-eth1 0')
    r2.cmd('ifconfig r2-eth0 192.168.20.254 netmask 255.255.255.0')
    r2.cmd('ifconfig r2-eth1 192.168.40.2 netmask 255.255.255.0')
    r2.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    r2.cmd('ip route add 192.168.10.0/24 via 192.168.40.1')
    # r3.cmd('ifconfig r3-eth0 0')
    # r3.cmd('ifconfig r3-eth1 0')
    # r3.cmd('ifconfig r3-eth0 192.168.30.254 netmask 255.255.255.0')
    # r3.cmd('ifconfig r3-eth1 192.168.40.3 netmask 255.255.255.0')
    # r3.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
    # r3.cmd('ip route add 192.168.10.0/24 via 192.168.40.1')

    h1.cmd('ifconfig h1-eth0 0')
    h1.cmd('ip addr add 192.168.10.1/24 brd + dev h1-eth0')
    h1.cmd('ip route add default via 192.168.10.254')
    h11.cmd('ifconfig h11-eth0 0')
    h11.cmd('ip addr add 192.168.10.11/24 brd + dev h11-eth0')
    h11.cmd('ip route add default via 192.168.10.254')
    h2.cmd('ifconfig h2-eth0 0')
    h2.cmd('ip addr add 192.168.20.1/24 brd + dev h2-eth0')
    h2.cmd('ip route add default via 192.168.20.254')
    # h3.cmd('ifconfig h3-eth0 0')
    # h3.cmd('ip addr add 192.168.30.1/24 brd + dev h3-eth0')
    # h3.cmd('ip route add default via 192.168.30.254')

    CLI(net)
    net.stop()
