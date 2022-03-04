#! /usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI

net = Mininet()

h1 = net.addHost('h1')
h2 = net.addHost('h2')
h3 = net.addHost('h3')

s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')
s3 = net.addSwitch('s3')


#create links from host to switch
net.addLink(h1, s1)
net.addLink(h2, s2)
net.addLink(h3, s3)

#create link between switches 
net.addLink(s1, s2) 
net.addLink(s2,s3)
net.addLink(s3,s1)


net.start()
#below just runs the emulation, and can exit with 'exit' command
CLI(net)
net.stop()

