from pox.pox.core import core
import pox.pox.openflow.libopenflow_01 as of
from pox.pox.lib.revent import *
from pox.pox.lib.revent.revent import EventMixin
from pox.pox.lib.util import dpidToStr
from pox.pox.lib.addresses import EthAddr
import os
import json
import pox.pox.lib.packet as packet

''' Add your imports here ... '''

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ['HOME']

''' Add your global variables here ... '''


class Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        config = self.read_config("rules.json")
        self.firewall_switch_id = config["firewall_switch_id"]
        self.rules = config["rules"]
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp(self, event):
        if event.dpid == self.firewall_switch_id:
            for rule in self.rules:
                self.add_rule(event, rule["rule"])

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

    def add_rule(self, event, rule):
        match = of.ofp_match()
        if "transport" in rule:
            self.add_transport_rule(rule["transport"], match)
        if "network" in rule:
            self.add_network_rule(rule["network"], match)

        msg = of.ofp_flow_mod()
        msg.match = match
        event.connection.send(msg)

    def read_config(self, file):
        file = open(file, "r")
        config = json.loads(file.read())
        file.close()
        return config

    def add_transport_rule(self, rule, match):
        if "src_port" in rule:
            match.tp_src = rule["src_port"]
        if "dst_port" in rule:
            match.tp_dst = rule["dst_port"]

    def add_network_rule(self, rule, match):
        if "ip_type" in rule:
            if "ipv4" == rule["ip_type"]:
                match.dl_type = packet.ethernet.IP_TYPE
            if "ipv6" == rule["ip_type"]:
                match.dl_type = packet.ethernet.IPV6_TYPE


def launch():
    '''
    Starting the Firewall module
    '''
    core.registerNew(Firewall)
