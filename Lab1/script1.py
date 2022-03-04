#! /usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI

net = Mininet()

h1 = net.addHost('h1')
h2 = net.addHost('h2')
h3 = net.addHost('h3')
h4 = net.addHost('h4')
h5 = net.addHost('h5')
h6 = net.addHost('h6')

s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')
s4 = net.addSwitch('s4')
s5 = net.addSwitch('s5')
s6 = net.addSwitch('s6')

#c0 = net.addController('c0')

net.addLink(h1, s1)
net.addLink(h2, s2)
net.addLink(h3, s3)
net.addLink(h4, s4)
net.addLink(h5, s5)
net.addLink(h6, s6)

#3rd and 4th parameter are the corresponding ports , aka h2 goes to 1 and s1 goes to 2
net.addLink(s2, s1) 

net.addLink(s3,s2)

net.addLink(s4,s3)

net.addLink(s5,s4)
net.addLink(s5,s2)
net.addLink(s5,s3)

net.addLink(s6,s5)
net.addLink(s6,s1)
net.addLink(s6,s2)


net.start()
#below just runs the emulation, and can exit with 'exit' command
CLI(net)
net.stop()

