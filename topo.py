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
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    r15 = net.addHost('r15', cls=Node, ip='0.0.0.0')
    r15.cmd('sysctl -w net.ipv4.ip_forward=1')
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    r13 = net.addHost('r13', cls=Node, ip='0.0.0.0')
    r13.cmd('sysctl -w net.ipv4.ip_forward=1')
    s16 = net.addSwitch('s16', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    r14 = net.addHost('r14', cls=Node, ip='0.0.0.0')
    r14.cmd('sysctl -w net.ipv4.ip_forward=1')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    r11 = net.addHost('r11', cls=Node, ip='0.0.0.0')
    r11.cmd('sysctl -w net.ipv4.ip_forward=1')
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch)
    r12 = net.addHost('r12', cls=Node, ip='0.0.0.0')
    r12.cmd('sysctl -w net.ipv4.ip_forward=1')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s17 = net.addSwitch('s17', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    WAN = net.addHost('WAN', cls=Host, ip='10.0.0.13', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    org_server = net.addHost('org_server', cls=Host, ip='10.0.0.10', defaultRoute=None)
    h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
    org_web = net.addHost('org_web', cls=Host, ip='10.0.0.9', defaultRoute=None)
    WAN2 = net.addHost('WAN2', cls=Host, ip='10.0.0.13', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s2, h4)
    net.addLink(s2, h3)
    net.addLink(s1, h2)
    net.addLink(s1, h1)
    net.addLink(s3, s2)
    net.addLink(s3, s1)
    net.addLink(s4, h8)
    net.addLink(s4, h7)
    net.addLink(s5, h6)
    net.addLink(s5, h5)
    net.addLink(s5, s6)
    net.addLink(s6, s4)
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
    net.addLink(r11, s6)
    net.addLink(r11, s3)
    net.addLink(WAN, s16)
    net.addLink(s16, r13)
    net.addLink(r14, s17)
    net.addLink(s17, WAN2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s4').start([c0])
    net.get('s6').start([c0])
    net.get('s5').start([c0])
    net.get('s16').start([])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s7').start([])
    net.get('s1').start([c0])
    net.get('s17').start([])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

