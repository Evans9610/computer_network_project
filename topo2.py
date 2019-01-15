#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   link=TCLink
                   )

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      protocol='tcp',
                      ip='127.0.0.1',
                      port=6633)

    info( '*** Add switches\n')
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s16 = net.addSwitch('s16', cls=OVSKernelSwitch)
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch)
    r13 = net.addHost('r13', cls=Node)
    r13.cmd('sysctl -w net.ipv4.ip_forward=1')
    r12 = net.addHost('r12', cls=Node)
    r12.cmd('sysctl -w net.ipv4.ip_forward=1')
    r11 = net.addHost('r11', cls=Node)
    r11.cmd('sysctl -w net.ipv4.ip_forward=1')
    s17 = net.addSwitch('s17', cls=OVSKernelSwitch)
    r15 = net.addHost('r15', cls=Node)
    r15.cmd('sysctl -w net.ipv4.ip_forward=1')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    r14 = net.addHost('r14', cls=Node)
    r14.cmd('sysctl -w net.ipv4.ip_forward=1')

    info( '*** Add hosts\n')
    WAN = net.addHost('WAN', cls=Host, ip='10.2.1.10/24', defaultRoute='via 10.2.1.1')
    org_web = net.addHost('org_web', cls=Host, ip='10.1.1.20', defaultRoute='via 10.1.1.1')
    h5 = net.addHost('h5', cls=Host, ip='10.0.2.20/24', defaultRoute='via 10.0.2.2')
    h6 = net.addHost('h6', cls=Host, ip='10.0.2.10/24', defaultRoute='via 10.0.2.1')
    h4 = net.addHost('h4', cls=Host, ip='10.0.1.10/24', defaultRoute='via 10.0.1.1')
    WAN2 = net.addHost('WAN2', cls=Host, ip='10.3.1.10/24', defaultRoute='via 10.3.1.1')
    h3 = net.addHost('h3', cls=Host, ip='10.0.1.20/24', defaultRoute='via 10.0.1.1')
    org_server = net.addHost('org_server', cls=Host, ip='10.1.1.10/24', defaultRoute='via 10.1.1.1')

    info( '*** Add links\n')
    net.addLink(s2, h4)
    net.addLink(s2, h3)
    net.addLink(s5, h6)
    net.addLink(s5, h5)
    net.addLink(s7, org_web)
    net.addLink(s7, org_server)
    net.addLink(r12, r15)
    net.addLink(r15, r13)
    net.addLink(r15, r14)
    net.addLink(r15, r11)
    net.addLink(r11, r14)
    net.addLink(r14, r13)
    net.addLink(r13, r12)
    net.addLink(r12, r11)
    net.addLink(r12, s7)
    net.addLink(WAN, s16)
    net.addLink(s16, r13)
    net.addLink(r14, s17)
    net.addLink(s17, WAN2)
    net.addLink(r11, s5)
    net.addLink(r11, s2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s5').start([c0])
    net.get('s16').start([])
    net.get('s7').start([])
    net.get('s17').start([])
    net.get('s2').start([c0])

    info( '*** Post configure switches and hosts\n')
    h5.cmd('vconfig add h5-eth0 101')
    h5.cmd('ifconfig h5-eth0.101 10.0.2.20/24')
    h6.cmd('vconfig add h6-eth0 100')
    h6.cmd('ifconfig h6-eth0.100 10.0.2.10/24')
    h4.cmd('vconfig add h4-eth0 100')
    h4.cmd('ifconfig h4-eth0.100 10.0.1.10/24')
    h3.cmd('vconfig add h3-eth0 101')
    h3.cmd('ifconfig h3-eth0.101 10.0.1.20/24')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

