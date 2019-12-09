#!/usr/bin/env python3.6
import sys
import struct

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import IP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from scapy.fields import *

routeA = False 

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print ("Cannot find eth0 interface")
        exit(1)
    return iface

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]
def handle_pkt(pkt):
    global routeA
    #print ("got a packet")
    iface = 'eth0'
    #print("RouteA eh " + str(routeA))
    #pkt.show2()
#    hexdump(pkt)
    sys.stdout.flush()
    pktAns = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff') 
    # Rota 1 vai por S3
    if routeA == True:
        pktAns = pktAns / SourceRoute(bos=0, port=1);
        routeA = False;
    # Rota 2 vai por S4
    elif routeA == False:
        pktAns = pktAns / SourceRoute(bos=0, port=2);
        routeA = True;

    pktAns = pktAns / SourceRoute(bos=0, port=1) / SourceRoute(bos=1,port=5);
    pktAns = pktAns / IP(dst='10.0.4.10') / UDP(dport=4321, sport=1234)
    sendp(pktAns, iface=iface, verbose=False)
    

class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("port", 0, 15)]
class SourceRoutingTail(Packet):
   fields_desc = [ XShortField("etherType", 0x800)]

bind_layers(Ether, SourceRoute, type=0x1234)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, SourceRoutingTail, bos=1)

def main():
    iface = 'eth0'
    print ("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="udp and port 4321", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
