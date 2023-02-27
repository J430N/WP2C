#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scapy.all import *
from scapy.layers.dot11 import Dot11


# set the interface name to monitor mode
interface = 'wlan0'
os.system(f'sudo ifconfig {interface} down')
os.system(f'sudo iwconfig {interface} mode monitor')
os.system(f'sudo ifconfig {interface} up')

# start sniffing for wireless devices
def sniff_devices(pkt):
    if pkt.haslayer(Dot11):
        if pkt.type == 0 and pkt.subtype == 8:
            # extract the MAC address of the device
            mac = pkt.addr2.upper()
            if mac not in devices:
                devices.append(mac)
                print(f"New device detected: {mac}")

devices = []
sniff(prn=sniff_devices, iface=interface)

# import nmap

# # create a new nmap scanner
# nm = nmap.PortScanner()

# # scan for devices on the access point's network
# access_point_ip = '192.168.0.1'
# nm.scan(hosts=f'{access_point_ip}/24', arguments='-sn')

# # print out the list of devices found
# for host in nm.all_hosts():
#     if 'mac' in nm[host]['addresses']:
#         mac = nm[host]['addresses']['mac'].upper()
#         print(f"Device found: {mac}")
