from mininet.topo import Topo


class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # if number_switches < 1:
        #    return #levantar excepcion

        s1 = self.addSwitch("switch_1")

        # for i in range(0, switches):
        #    switches.append(self.addSwitch("switch_1"))

        # Create hosts
        h1 = self.addHost("host_1")
        h2 = self.addHost("host_2")
        #        h3 = self.addHost("host_3")
        #        h3 = self.addHost("host_4")

        # Add links between switches and hosts self
        self.addLink(s1, h1)
        self.addLink(s1, h2)

        # self.addLink(s2, h3)
        # self.addLink(s2, h4)


topos = {'customTopo': MyTopo}
