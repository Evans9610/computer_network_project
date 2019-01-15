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
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }
controller = None

def exampleAllHosts( vlan ):
    """Simple example of how VLANHost can be used in a script"""
    # This is where the magic happens...
    host = partial( VLANHost, vlan=vlan )
    # vlan (type: int): VLAN ID to be used by all hosts

    # Start a basic network using our VLANHost
    topo = SingleSwitchTopo( k=2 )
    net = Mininet( host=host, topo=topo )
    net.start()
    CLI( net )
    net.stop()

# pylint: disable=arguments-differ

class VLANStarTopo( Topo ):
    """Example topology that uses host in multiple VLANs
       The topology has a single switch. There are k VLANs with
       n hosts in each, all connected to the single switch. There
       are also n hosts that are not in any VLAN, also connected to
       the switch."""

    def build( self, k=2, n=2, vlanBase=100 ):
        s1 = self.addSwitch( 's1' )
        for i in range( k ):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % ( j+1, vlan )
                h = self.addHost( name, cls=VLANHost, vlan=vlan )
                self.addLink( h, s1 )
        for j in range( n ):
            h = self.addHost( 'h%d' % (j+1) )
            self.addLink( h, s1 )

def exampleCustomTags():
    """Simple example that exercises VLANStarTopo"""

    net = Mininet( topo=VLANStarTopo() )

    c1 = net.addController(name="c1", controller=RemoteController, ip="127.0.0.1", port=8787)
    net.start()
    c1.start()
    net.get('s1').start([c1])
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
