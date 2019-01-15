from mininet.node import Host
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.log import error
from mininet.node import RemoteController

class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        newName = '%s.%d' % ( intf, vlan )
        intf.name = newName
        self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }

class VLANStarTopo( Topo ):
    def build( self, k=2, n=2, vlanBase=100 ):
        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        self.addLink( s1, s2 )
        self.addLink( s1, s3 )
        self.addLink( s2, s5 )
        self.addLink( s2, s4 )
        self.addLink( s2, s3 )
        self.addLink( s3, s4 )
        self.addLink( s4, s5 )

        vlan_list = [100, 200, 100, 200, 100, 200, 100, 200]
        h1 = self.addHost( 'h1', cls=VLANHost, vlan=vlan_list[0])
        self.addLink( h1, s3 )
        h2 = self.addHost( 'h2', cls=VLANHost, vlan=vlan_list[1])
        self.addLink( h2, s3 )
        h3 = self.addHost( 'h3', cls=VLANHost, vlan=vlan_list[2])
        self.addLink( h3, s4 )
        h4 = self.addHost( 'h4', cls=VLANHost, vlan=vlan_list[3])
        self.addLink( h4, s1 )
        h5 = self.addHost( 'h5', cls=VLANHost, vlan=vlan_list[4])
        self.addLink( h5, s5 )
        h6 = self.addHost( 'h6', cls=VLANHost, vlan=vlan_list[5])
        self.addLink( h6, s2 )
        h7 = self.addHost( 'h7', cls=VLANHost, vlan=vlan_list[6])
        self.addLink( h7, s2 )
        h8 = self.addHost( 'h8', cls=VLANHost, vlan=vlan_list[7])
        self.addLink( h8, s5 )


def exampleCustomTags():

    net = Mininet( topo=VLANStarTopo() )
    c1 = net.addController(name="c1", controller=RemoteController, ip="127.0.0.1", port=8787)
    net.start()
    c1.start()
    net.get('s1').start([c1])
    net.get('s2').start([c1])
    net.get('s4').start([c1])
    net.get('s5').start([c1])
    net.get('s3').start([c1])
    CLI( net )
    net.stop()

if __name__ == '__main__':
    import sys
    from functools import partial

    from mininet.net import Mininet
    from mininet.cli import CLI
    from mininet.topo import SingleSwitchTopo
    from mininet.log import setLogLevel

    setLogLevel( 'info' )

    if not quietRun( 'which vconfig' ):
        error( "Cannot find command 'vconfig'\nThe package",
               "'vlan' is required in Ubuntu or Debian,",
               "or 'vconfig' in Fedora\n" )
        exit()

    if len( sys.argv ) >= 2:
        exampleAllHosts( vlan=int( sys.argv[ 1 ] ) )
    else:
        exampleCustomTags()
