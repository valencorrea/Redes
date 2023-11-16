from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent.revent import EventMixin
from pox.lib.util import dpidToStr
from pox.lib.addresses import EthAddr
import os
import json

''' Add your imports here ... '''

log = core.getLogger()
policyFile = "%s/pox/pox/misc/firewall-policies.csv" % os.environ['HOME']

''' Add your global variables here ... '''


class Firewall(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        config = self.read_config("/home/valen/redes/Redes/TP2/rules.json")
        self.firewall_switch_id = config["firewall_switch_id"]
        self.rules = config["rules"]
        log.debug("Enabling Firewall Module")

    def _handle_ConnectionUp(self, event):  # -> ver
        if event.dpid == self.firewall_switch_id:
            for rule in self.rules:
                self.add_rule(event, ["rule"])

        log.debug("Firewall rules installed on %s", dpidToStr(event.dpid))

    def add_rule(self, event, rule):
        match = of.ofp_match()
        log.debug("Adding firewall rule")

        if "dst_port" in rule:
            match.tp_dst = rule["dst_port"]
        if "protocol" in rule:
            match.nw_proto = rule["protocol"]
        if "dl_src" in rule["dl_src"]:
            match.dl_src = EthAddr(rule["dl_src"])
        if "dl_dst" in rule["dl_dst"]:
            match.dl_dst = EthAddr(rule["dl_dst"])

        msg = of.ofp_flow_mod()
        msg.match = match
        event.connection.send(msg)

    def read_config(self, file):
        file = open(file, "r")
        config = json.loads(file.read())
        file.close()
        return config


def launch():
    """
    Starting the Firewall module
    """
    core.registerNew(Firewall)
