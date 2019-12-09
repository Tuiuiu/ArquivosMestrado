#!/usr/bin/env python2

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-hosts', help='Number of hosts to connect to switch',
                    type=int, action="store", default=6)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()


class TestFourSwitches(Topo):
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, n, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        thriftport = thrift_port
        switch1 = self.addSwitch('s1', 
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thriftport,
                                pcap_dump = pcap_dump)
        thriftport = thriftport + 1
        switch2 = self.addSwitch('s2', 
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thriftport,
                                pcap_dump = pcap_dump)
        thriftport = thriftport + 1
        switchmeio1 = self.addSwitch('s3', 
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thriftport,
                                pcap_dump = pcap_dump)
        thriftport = thriftport + 1
        switchmeio2 = self.addSwitch('s4', 
                                sw_path = sw_path,
                                json_path = json_path,
                                thrift_port = thriftport,
                                pcap_dump = pcap_dump)
        host1 = self.addHost('h1',
                            ip = "10.0.0.10/24", 
                            mac='00:04:00:00:00:00')
        host2 = self.addHost('h2', 
                            ip = "10.0.1.10/24",
                            mac='00:04:00:00:00:01')
        host3 = self.addHost('h3', 
                            ip = "10.0.2.10/24",
                            mac='00:04:00:00:00:02') 
        host4 = self.addHost('h4', 
                            ip = "10.0.3.10/24",
                            mac='00:04:00:00:00:03')
        hostfonte = self.addHost('h5',
                                ip = "10.0.4.10/24",
                                mac='00:04:00:00:00:04',
                                inNamespace=False)
        hostsorve = self.addHost('h6',
                                ip = "10.0.5.10/24",
                                mac='00:04:00:00:00:05')
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(switch1, switchmeio1, delay="10ms")
        self.addLink(switch1, switchmeio2, delay="30ms")
        self.addLink(switch2, switchmeio1, delay="10ms")
        self.addLink(switch2, switchmeio2, delay="30ms")
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)
        self.addLink(hostfonte, switch1)
        self.addLink(hostsorve, switch2)


def main():
    num_hosts = args.num_hosts
    mode = args.mode

    topo = TestFourSwitches(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            num_hosts)
    net = Mininet(topo = topo,
                  link=TCLink,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)
    net.start()



    sw_mac = ["00:aa:bb:00:00:%02x" % n for n in xrange(num_hosts)]

    sw_addr = ["10.0.%d.1" % n for n in xrange(num_hosts)]

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        if mode == "l2":
            h.setDefaultRoute("dev eth0")
        else:
            h.setARP(sw_addr[n], sw_mac[n])
            h.setDefaultRoute("dev eth0 via %s" % sw_addr[n])

    for n in xrange(num_hosts):
        h = net.get('h%d' % (n + 1))
        h.describe()

    sleep(1)

    print "Ready !"

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()
