#!/usr/bin/python



"""

Script created by VND - Visual Network Description (SDN version)

"""

from mininet.net import Mininet

from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch

from mininet.cli import CLI

from mininet.log import setLogLevel

from mininet.link import Link, TCLink



def topology():

    "Create a network."

    net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )



    print "*** Creating nodes"

    h1 = net.addHost( 'h1', mac='00:00:00:00:00:01', ip='10.0.0.1/8' )

    h2 = net.addHost( 'h2', mac='00:00:00:00:00:02', ip='10.0.0.2/8' )

    s3 = net.addSwitch( 's3', listenPort=6634, mac='00:00:00:00:00:03' )

    s4 = net.addSwitch( 's4', listenPort=6635, mac='00:00:00:00:00:04' )

    s5 = net.addSwitch( 's5', listenPort=6636, mac='00:00:00:00:00:05' )

    s6 = net.addSwitch( 's6', listenPort=6637, mac='00:00:00:00:00:06' )

    c7 = net.addController( 'c7', controller=RemoteController, ip='127.0.0.1', port=6633 )



    print "*** Creating links"

    net.addLink(s4, h2, 3, 0)

    net.addLink(s6, s4, 2, 2)

    net.addLink(s5, s6, 2, 1)

    net.addLink(s3, s5, 3, 1)

    net.addLink(s3, s4, 2, 1)

    net.addLink(h1, s3, 0, 1)



    print "*** Starting network"

    net.build()

    s4.start( [c7] )

    s6.start( [c7] )

    s5.start( [c7] )

    s3.start( [c7] )

    c7.start()



    print "*** Running CLI"

    CLI( net )



    print "*** Stopping network"

    net.stop()



if __name__ == '__main__':

    setLogLevel( 'info' )

    topology()
