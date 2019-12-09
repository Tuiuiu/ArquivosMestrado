#!/usr/bin/env python3.6
import argparse
import sys
import socket
import random
import struct
import subprocess

from scapy.all import sniff, sendp, send, srp1, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP
from scapy.fields import *
import readline

from datetime import datetime, timedelta

timestart = 0
timesentA = datetime.now()
timesentB = datetime.now()
latencyA = 2000
latencyB = 2000
routeA = False
selectedRoute = 'A'
#timestop = 0

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print ("Cannot find eth0 interface")
        exit(1)
    return iface

class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("port", 0, 15)]

bind_layers(Ether, SourceRoute, type=0x1234)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, IP, bos=1)

def start_tables():
    p = subprocess.run(["sh", "populate_tables.sh"])

def swap_route_A(foundTime):
    global selectedRoute
    p = subprocess.run(["sh", "set_route_A.sh"])
    settime = datetime.now()
    selectedRoute = 'A'
    time_experiment(foundTime, settime)

def swap_route_B(foundTime):
    global selectedRoute
    p = subprocess.run(["sh", "set_route_B.sh"])
    settime = datetime.now()
    selectedRoute = 'B'
    time_experiment(foundTime, settime)

def time_experiment(foundTime, setTime):
    print("Momento em que encontrou a anomalia:")
    print(foundTime)
    print("Momento em que mudou as rotas:")
    print(setTime)
    sys.stdout.flush()

def handle_pkt(pkt):  
    timereceived = datetime.now()
    global timestart, routeA, timesentA, timesentB, latencyA, latencyB, selectedRoute;
    #print ("got an answer")
    timedelta_start = timereceived - timestart
    timedelta_seconds = 0

    #total = timedelta.seconds * 1000 + timedelta.microseconds / 1000.0
    #timestamp = timedelta_start.seconds * 1000 + timedelta_start.microseconds / 1000.0
    timestamp = timedelta_start.seconds + timedelta_start.microseconds / 1000000.0

    if routeA == True:
        #print "A rota A possui latencia de %s milisegundos" % total
        #fileA.write("Timestamp: %s Latency: %s \n" % (timestamp, total))
        
        #Calcula a latencia do caminho A
        timedelta = timereceived - timesentA
        latencyA = timedelta.seconds * 1000 + timedelta.microseconds / 1000.0
        if (selectedRoute == 'A' and latencyA > 500 and latencyB <= 500):
            foundtime = datetime.now()
            swap_route_B(foundtime)
        #Grava o valor do timestamp e da latencia no arquivo relativo 
        fileA.write("%s %s \n" % (timestamp, latencyA))
        routeA = False
        timedelta_miliseconds = latencyA
    else:
        #print "A rota B possui latencia de %s milisegundos" % total
        #fileB.write("Timestamp: %s Latency: %s \n" % (timestamp, total))

        #Calcula a latencia do caminho B
        timedelta = timereceived - timesentB
        latencyB = timedelta.seconds * 1000 + timedelta.microseconds / 1000.0
        if (selectedRoute == 'B' and latencyB > 500 and latencyA <= 500):
            foundtime = datetime.now()
            swap_route_A(foundtime)
        #Grava o valor do timestamp e da latencia no arquivo relativo
        fileB.write("%s %s \n" % (timestamp, latencyB))
        routeA = True
        timedelta_miliseconds = latencyB
    #print "Sleep for a while"
    if (timedelta_miliseconds < 500):
        tempo = 0.5 - (timedelta_miliseconds/1000.0)
        time.sleep(tempo)
    addr = '10.0.5.10'
    iface = get_if()
    send_probe1(addr, iface)

def send_probe1(addr, iface):
    global timesent, routeA, timesentA, timesentB;
    pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff');
    #rota 1 -> Fonte S1 S3 S2 H5
    if routeA == True:
        pkt = pkt / SourceRoute(bos=0, port=3)
    # rota 2 -> Fonte S1 S4 S2 H5
    elif routeA == False:
        pkt = pkt / SourceRoute(bos=0, port=4)
    # Rota 3 -> Fonte S1 S3 S2 S4 S1 S3 S2 H5
    #pkt = pkt / SourceRoute(bos=0, port=3) / SourceRoute(bos=0,port=2) / SourceRoute(bos=0, port=2) / SourceRoute(bos=0, port=1) / SourceRoute(bos=0, port=3) / SourceRoute(bos=0, port=2) / SourceRoute(bos=1, port=5)
    pkt = pkt / SourceRoute(bos=0,port=2) / SourceRoute(bos=1,port=5)
    pkt = pkt / IP(dst=addr) / UDP(dport=4321, sport=1234)
    
    #print("Sending packet")
    if(routeA == True):
        timesentA = datetime.now()
    elif(routeA == False):
        timesentB = datetime.now()
    #timesent = datetime.now()
    sendp(pkt, iface=iface, verbose=False)

def main():

    #if len(sys.argv)<2:
    #    print 'pass 2 arguments: <destination>'
    #    exit(1)

    global fileA 
    global fileB 

    global timestart

    fileA = open("routeA.txt", "w+")
    fileB = open("routeB.txt", "w+")


    #addr = socket.gethostbyname(sys.argv[1])
    
    #Set the addr to the Sink IP
    addr = '10.0.5.10'
    iface = get_if()
    #iface = "eth0"
    print ("sending on interface %s to %s" % (iface, str(addr)))

    start_tables()
    
    #while(True):
    #    time.sleep(5)
    #    swap_route_B()
    #    time.sleep(5)
    #    swap_route_A()

    timestart = datetime.now()


    send_probe1(addr, iface)
    sniff(filter="udp and port 4321", iface=iface, 
          prn = lambda x: handle_pkt(x))
    
if __name__ == '__main__':
    main()
