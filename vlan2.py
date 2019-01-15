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
        s1 = self.addSwitch( 's1', mac="ff:00:00:00:00:01" )
        s2 = self.addSwitch( 's2', mac="ff:00:00:00:00:02" )
        s3 = self.addSwitch( 's3', mac="ff:00:00:00:00:03" )
        h1 = self.addHost( 'h1-100', cls=VLANHost, vlan=vlan )
        h2 = self.addHost( 'h2-100', cls=VLANHost, vlan=vlan )
        self.addLink( h1, s1 )
        self.addLink( h2, s2 )
        self.addLink( s1, s2 )
        self.addLink( s2, s3 )
        self.addLink( s1, s3 )


def exampleCustomTags():

    net = Mininet( topo=VLANStarTopo() )
    c1 = net.addController(name="c1", controller=RemoteController, ip="127.0.0.1", port=6633)
    net.start()
    c1.start()
    net.get('s1').start([c1])
    net.get('s2').start([c1])
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