from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
import time

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0
block_list = {}

class LearningSwitch (object):
    def __init__ (self, connection, transparent):
        # Switch we'll be adding    L2 learning switch capabilities to
        self.connection = connection
        self.transparent = transparent

        # Our table
        self.macToPort = {}

        # We want to hear PacketIn messages, so we listen
        # to the connection
        connection.addListeners(self)

        # We just use this to know when to log a helpful message
        self.hold_down_expired = _flood_delay == 0

        # log.debug("Initializing LearningSwitch, transparent=%s",
        #                    str(self.transparent))
    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """

        packet = event.parsed
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            if time.time() - self.connection.connect_time >= _flood_delay:
                # Only flood if we've been connected for a little while...

                if self.hold_down_expired is False:
                    # Oh yes it is!
                    self.hold_down_expired = True
                    log.info("%s: Flood hold-down expired -- flooding",
                            dpid_to_str(event.dpid))

                if message is not None: log.debug(message)
                # log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
                # OFPP_FLOOD is optional; on some switches you may need to change
                # this to OFPP_ALL.
                msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            else:
                pass
                #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
            msg.data = event.ofp
            msg.in_port = event.port
            self.connection.send(msg)

        def drop (duration = None):
            """
            Drops this packet and optionally installs a flow to continue
            dropping similar ones for a while
            """
            if duration is not None:
                if not isinstance(duration, tuple):
                    duration = (duration,duration)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = duration[0]
                msg.hard_timeout = duration[1]
                msg.buffer_id = event.ofp.buffer_id
                self.connection.send(msg)
            elif event.ofp.buffer_id is not None:
                msg = of.ofp_packet_out()
                msg.buffer_id = event.ofp.buffer_id
                msg.in_port = event.port
                self.connection.send(msg)

        self.macToPort[packet.src] = event.port # 1
        now = int(time.time())
        # prevent to block switch traffic from port 1
        if packet.src.to_str() in block_list and event.port != 1:
            if now - block_list[packet.src.to_str()]['timestamp'] > 30:
                # timeout, release the block_list
                block_list.pop(packet.src.to_str())
                log.info("rule blocking {} expired, removed from block_list".format(packet.src.to_str()))
            else:
                print("{} has been blocked".format(packet.src))
                # if attack continued then refresh the block rule
                block_list[packet.src.to_str()]['timestamp'] = int(time.time())
                drop()
                return
                # drop((5, 10))       # idle_timeout, hard_timeout

        if not self.transparent: # 2
            if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
                drop() # 2a
                return

        if packet.dst.is_multicast:
            flood() # 3a
        else:
            if packet.dst not in self.macToPort: # 4
                flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
            else:
                port = self.macToPort[packet.dst]
                if port == event.port: # 5
                    # 5a
                    log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
                            % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
                    drop(10)
                    return
                # 6
                log.debug("installing flow for %s.%i -> %s.%i" %
                                    (packet.src, event.port, packet.dst, port))
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet, event.port)
                msg.idle_timeout = 10
                msg.hard_timeout = 30
                msg.actions.append(of.ofp_action_output(port = port))
                msg.data = event.ofp # 6a
                self.connection.send(msg)


class l2_learning (object):
    """
    Waits for OpenFlow switches to connect and makes them learning switches.
    """
    def __init__ (self, transparent):
        core.openflow.addListeners(self)
        self.transparent = transparent

    def _handle_ConnectionUp (self, event):
        log.debug("Connection %s" % (event.connection,))
        LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay):
    """
    Starts an L2 learning switch.
    """
    try:
        global _flood_delay
        _flood_delay = int(str(hold_down), 10)
        assert _flood_delay >= 0
    except:
        raise RuntimeError("Expected hold-down to be a number")

    core.registerNew(l2_learning, str_to_bool(transparent))

    def _timer_func ():
        for connection in core.openflow._connections.values():
            connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
            connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
        log.debug("Sent %i flow/port stats request(s)", len(core.openflow._connections))

    def _handle_flowstats_received (event):
        # stats = flow_stats_to_list(event.stats)
        # log.debug("FlowStatsReceived from %s: %s", dpidToStr(event.connection.dpid), stats)

        traffics = {}       # mac: [src_ip, src_port, byte_count, packet_count]
        for f in event.stats:
            if f.match.nw_src is None:      # ignore switch traffic
                continue
            src_ip = f.match.nw_src.toStr()
            src_mac = f.match.dl_src.to_str()
            src_port = f.match.in_port      # from switch

            # adding timestamp
            traffics[src_mac] = {'src_ip': src_ip, 'src_port': src_port,
            'byte_count': f.byte_count, 'packet_count': f.packet_count, 'timestamp': int(time.time())}

        for mac in traffics:
            if traffics[mac]['packet_count'] > 10:# and traffics[ip]['byte_count'] > 1024 * 64:
                log.info("IP: {} triggered packet block. Switch will block host 30 seconds.".format(mac))
                block_list[mac] = traffics[mac]

        # print("block list: {}".format(",".join([x for x in block_list])))
        # log.info("Traffic from %s: %s bytes (%s packets) over %s flows",
        #     dpidToStr(event.connection.dpid), bytes_count, packet_count, flows_count)

    # port stats handler
    # def _handle_portstats_received (event):
    #     stats = flow_stats_to_list(event.stats)
    #     log.debug("PortStatsReceived from %s: %s",
    #         dpidToStr(event.connection.dpid), stats)

    from pox.lib.recoco import Timer

    # attach handsers to listners
    core.openflow.addListenerByName("FlowStatsReceived",
        _handle_flowstats_received)

    # disable port stats
    # core.openflow.addListenerByName("PortStatsReceived",
    #     _handle_portstats_received)

    # timer set to execute every five seconds
    Timer(5, _timer_func, recurring=True)
