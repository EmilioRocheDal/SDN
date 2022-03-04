#!/usr/bin/python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class CustomTopo(Topo):

	def __init__(self):
		#Initialize Topo object
		Topo.__init__(self)
		
		#Instantiate hosts and switches
		switchIds = []
		
		for d in range(8):
			host = self.addHost('h%s' %(d+1))
			switch = self.addSwitch('s%s' %(d+1))
			switchIds.append(switch)
			self.addLink(host, switch)
		
		edgeList = [(1,2),(1,3),(2,3),(3,4),(4,5),(4,6),(4,7),(5,6),(5,8)]
		
		for link in edgeList:
			#Switch indexes go from 0 to n-1
			self.addLink(switchIds[link[0]-1], switchIds[link[1]-1])

def runner():
	#create and run a custom topo
	myTopo = CustomTopo()
	net = Mininet(myTopo)
	net.start()
	CLI(net)
	net.stop()

if __name__ == '__main__':
	runner()
