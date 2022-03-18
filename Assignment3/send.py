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

    iface_list = ['veth0','veth2','veth4','veth6']
    ethernet_list = ['00:00:00:00:00:01','00:00:00:00:00:02','00:00:00:00:00:03','00:00:00:00:00:04']
    ip_list = ['10.0.0.1','10.0.0.2','10.0.0.3','10.0.0.4']
    pairs = [[1,2],[2,1],[1,3],[3,1],[1,4],[4,1],[2,3],[3,2],[2,4],[4,2],[3,4],[4,3]]

    for i, j in pairs:
        iface = iface_list[i-1]
        ethSrc = ethernet_list[i-1]
        ethDst = ethernet_list[j-1]
        ipOne = ip_list[j-1]
        ipDst = socket.gethostbyname(ipOne)
        ipTwo = ip_list[i-1]
        ipSrc = socket.gethostbyname(ipTwo)
        message = "My message"
        print "sending to interfaces"
        pkt =  Ether(src=ethSrc, dst=ethDst)
        pkt = pkt /IP(src=ipSrc,dst=ipDst) / UDP(dport=1234, sport=random.randint(49152,65535)) / message
        pkt.show2()
        sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
