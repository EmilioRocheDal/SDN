#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP


def main():

    iface_list = ['veth2','veth4','veth6','veth6']
    ethernet_list = ['00:00:00:00:00:01','00:00:00:00:00:02','00:00:00:00:00:03','00:00:00:00:00:04']
    ip_list = ['10.0.0.1','10.0.0.2','10.0.0.3','10.0.0.4']
    pairs = [[1,2][1,3][1,4][2,3][2,4][3,4]]

    if len(sys.argv)<1:
        print 'pass 1 arguments: "<message>"'
        exit(1)


    print "sending on interface %s to %s" % (iface, str(addr))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(src=srcAddr, dst=dstAddr) / UDP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
