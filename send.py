#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sniff, sendp, send, srp1, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP
from scapy.fields import *
import readline

from datetime import datetime, timedelta

timestart = 0
timesent = 0
routeA = True
#timestop = 0

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("port", 0, 15)]

bind_layers(Ether, SourceRoute, type=0x1234)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, IP, bos=1)

def handle_pkt(pkt):  
    timereceived = datetime.now()
    global timestart, timesent, routeA;

    #print "got an answer"
    timedelta = timereceived - timesent
    timedelta_start = timereceived - timestart
    
    total = timedelta.seconds * 1000 + timedelta.microseconds / 1000.0
    #timestamp = timedelta_start.seconds * 1000 + timedelta_start.microseconds / 1000.0
    timestamp = timedelta_start.seconds + timedelta_start.microseconds / 1000000.0

    if routeA == True:
        #print "A rota A possui latencia de %s milisegundos" % total
        #fileA.write("Timestamp: %s Latency: %s \n" % (timestamp, total))
        fileA.write("%s %s \n" % (timestamp, total))
        routeA = False
    else:
        #print "A rota B possui latencia de %s milisegundos" % total
        #fileB.write("Timestamp: %s Latency: %s \n" % (timestamp, total))
        fileB.write("%s %s \n" % (timestamp, total))
        routeA = True
    #pkt.show()
    #print "Sleep for a while"
    time.sleep(0.5)
    addr = '10.0.0.21'
    iface = get_if()
    send_probe1(addr, iface)

def send_probe1(addr, iface):
    global timesent, routeA;
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff');
    #rota 1 -> Fonte S1 S3 S2 H5
    if routeA == True:
        pkt = pkt / SourceRoute(bos=0, port=3) / SourceRoute(bos=0,port=2) / SourceRoute(bos=1, port=5)
    # rota 2 -> Fonte S1 S4 S2 H5
    else:
        pkt = pkt / SourceRoute(bos=0, port=4) / SourceRoute(bos=0,port=2) / SourceRoute(bos=1, port=5)
    # Rota 3 -> Fonte S1 S3 S2 S4 S1 S3 S2 H5
    #pkt = pkt / SourceRoute(bos=0, port=3) / SourceRoute(bos=0,port=2) / SourceRoute(bos=0, port=2) / SourceRoute(bos=0, port=1) / SourceRoute(bos=0, port=3) / SourceRoute(bos=0, port=2) / SourceRoute(bos=1, port=5)
    pkt = pkt / IP(dst=addr) / UDP(dport=4321, sport=1234)
    #pkt.show2()
    #print "send a probe packet"
    sendp(pkt, iface=iface, verbose=False)
    timesent = datetime.now()

def main():

    #if len(sys.argv)<2:
    #    print 'pass 2 arguments: <destination>'
    #    exit(1)

    global fileA 
    global fileB 

    global timestart

    fileA = open("routeA.txt", "w+")
    fileB = open("routeB.txt", "w+")

    timestart = datetime.now()

    #addr = socket.gethostbyname(sys.argv[1])
    #Set the addr to the Sink IP
    addr = '10.0.0.21'
    iface = get_if()
    print "sending on interface %s to %s" % (iface, str(addr))

    

#    while True:
#        print
#        s = str(raw_input('Type space separated port nums '
#                          '(example: "2 3 2 2 1") or "q" to quit: '))
#        if s == "q":
#            break;
#        print

#        i = 0
#        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff');
#        for p in s.split(" "):
#            try:
#                pkt = pkt / SourceRoute(bos=0, port=int(p))
#                i = i+1
#            except ValueError:
#                pass
#        if pkt.haslayer(SourceRoute):
#            pkt.getlayer(SourceRoute, i).bos = 1

#        pkt = pkt / IP(dst=addr) / UDP(dport=4321, sport=1234)
#        pkt.show2()
#        ans = srp1(pkt, iface=iface, verbose=False)
#        if ans:
#            ans.show2()

    send_probe1(addr, iface)

    sniff(filter="udp and port 4321", iface = iface, 
          prn = lambda x: handle_pkt(x))

    #pkt = pkt / SourceRoute(bos=0, port=2) / SourceRoute(bos=0, port=3);
    #pkt = pkt / SourceRoute(bos=0, port=2) / SourceRoute(bos=0, port=2);
    #pkt = pkt / SourceRoute(bos=1, port=1)


if __name__ == '__main__':
    main()
