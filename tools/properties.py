#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Developer Name: Mr. Jason Teo Jie Chen
# Program Name: properties.py
# Description: Display basic Wi-Fi properties and devices connected to the network
# First Written On: 2 March 2023
# Edited On: 21 March 2023

import ipaddress
import socket
import requests
from .iw import Iw
from util.color import Color
from config import Configuration
from util.process import Process


class Properties:
    """Get properties of WiFi networks."""
    # Configuration.initialize(False)
 
    dict_list = []
    local_ipv4_add = None
    
    @classmethod
    def run(cls):
        """Run the properties module."""
        
        # Get the public IPv4 and IPv6 address
        try:
            response = requests.get('https://api.ipify.org')
            Properties.pub_ipv4_add = response.text
        except:
            Properties.pub_ipv4_add = 'N/A'
  
        try:
            response = requests.get('https://api64.ipify.org')
            Properties.pub_ipv6_add = response.text
        except:
            Properties.pub_ipv6_add = 'N/A'
        
        if not Properties.get_network_info() is False and len(Properties.dict_list) > 0:
            Color.pl('\n{W}------------------------------------{G} Wi-Fi Properties {W}-----------------------------------')
            for dict in cls.dict_list:
                for key, value in dict.items():
                    Color.p('{+} {W}%s: ' % str(key).ljust(19))
                    Color.pl('{C}%s' % str(value))

                # print out the infomations of the founded devices and the summary               
                if Properties.local_ipv4_add is not None:
                    Color.pl('\n{+} {W}Discovering devices on the {C}%s {W}network...' % Properties.dict_list[0]['SSID'])               
                    Color.pl('\n{+} {W}Devices Connected to {G}%s {W}:' % Properties.dict_list[0]['SSID'])
                    attribute = ['Name', 'MAC Address', 'Manufacturer']
                    count = 0
                        
                    for element in Properties.discovery(Properties.local_ipv4_add):
                        if Properties.valid_ip(element): # Check if the element is a IP address or not
                            Color.p('{+} IP Address         : ')
                            Color.pl('{C}%s' % element)
                            count = 1
                            continue
                        elif count == 1:
                            Color.p('{+} %s               : ' % attribute[0])
                            Color.pl('{C}%s' % element)
                            count += 1
                            continue
                        elif count == 2:
                            Color.p('{+} %s        : ' % attribute[1])
                            Color.pl('{C}%s' % element)
                            count += 1
                            continue
                        elif count == 3:
                            Color.p('{+} %s       : ' % attribute[2])
                            Color.pl('{C}%s' % element + '\n')
                            continue
                        
                    Color.p('\n{+} Summary            : ')
                    Color.pl('{C}Found {O}%d{C} devices on the {O}' % Properties.host + Properties.network_ip + '{C} network{W}')

            Color.pl('{W}--------------------------------------- {G}Thank You {W}---------------------------------------')
            Configuration.exit_gracefully()
                    
        else:
            Color.pl('{!} {R}Error: WP2C {O}could not find any wireless interfaces{W}')
            Configuration.exit_gracefully()

                    
    @staticmethod
    def get_network_info():
        
        interfaces = Iw.get_interfaces()
        
        if len(interfaces) == 0:
            return False
        else:
            # First row: columns
            Color.p('   NUM')
            Color.pl('  Wireless Interface')
            Color.p('   ---')
            Color.pl('  ------------------')
            
            # Remaining rows: interfaces
            for idx, interface in enumerate(interfaces, start=1): #Adjust here
                Color.clear_entire_line()
                Color.p('   {G}%s ' % str(idx).ljust(3)) #numuber to left only (need all to left)
                Color.pl('{B}%s' % str(interface).ljust(3))

            input_str = '{+} Select target(s)'
            input_str += ' ({G}1-%d{W})' % len(interfaces)
            input_str += ' separated by commas, dashes'
            input_str += ' or {G}all{W}: '

            chosen_interfaces = []

            Color.p(input_str)
            for choice in input().split(','):
                choice = choice.strip()
                if choice.lower() == 'all':
                    chosen_interfaces = interfaces
                    break
                if '-' in choice:
                    if choice.startswith('-'):
                        Color.pl('    {!} {O}Invalid target index (%s)... ignoring' % choice)
                        continue
                    # User selected a range
                    (lower, upper) = [int(x) for x in choice.split('-')]
                    if lower < 1 or lower > len(interfaces) or upper < 1 or upper > len(interfaces):
                        Color.pl('    {!} {O}Invalid target index (%s)... ignoring' % choice)
                        continue
                    else:
                        lower -= 1
                        upper -= 1
                        for i in range(lower, min(len(interfaces), upper + 1)):
                            chosen_interfaces.append(interfaces[i])
                elif choice.isdigit() and int(choice) <= len(interfaces) and int(choice)> 0:
                    chosen_interfaces.append(interfaces[int(choice) - 1])
                else:
                    Color.pl('    {!} {O}Invalid target index (%s)... ignoring' % choice)
                    continue
            
            # Get WiFi properties from chosen interfaces        
            for interface in chosen_interfaces:
                interface = interface.strip()
  
                dict = {} # Create a dict for each wireless interface
                dict['Wireless Interface'] = interface        

                try:
                    # Get WiFi properties using iwconfig         
                    p = Process('iwconfig ' + interface)
                    lines = p.stdout().split('\n')
                    for line in lines:
                        if 'ESSID' in line:
                            ssid = line.split('ESSID:')[1].split('"')[1]
                            dict['SSID'] = ssid
                            
                        if '802.11' in line:
                            protocol = line.split()[2]
                            dict['Protocol'] = protocol
                            
                        if 'Frequency' in line:
                            frequency = line.split('Frequency:')[1].split()[0]
                            dict['Frequency'] = frequency + ' Ghz'
                            
                        if ('Frequendcy' in dict or 'Link Quality' in line or line == lines[-1]):
                            dict.update(Properties.get_network_info_cont(ssid))
                        
                        if 'Access Point' in line:
                            mac = line.split('Access Point:')[1].strip()
                            dict['MAC Address'] = mac
                            
                            oui = ''.join(mac.split(':')[:3]) # Use oui in MAC address to find manufacturer                       
                            manufacturer = Configuration.manufacturers.get(oui, "")
                            dict['Manufacturer'] = manufacturer 
                            
                        if 'Link Quality' in line:
                            quality = line.split('Link Quality=')[1].split()[0]
                            dict['Link Quality'] = quality
                            
                        if 'Signal level' in line:
                            signal_level = line.split('Signal level=')[1].split()[0]
                            dict['Signal Level'] = signal_level
                            
                    Properties.dict_list.append(dict) # Add dict to list
                    
                except:
                    Color.pl('{!} {R}Error: Unable to obtain Wi-Fi properties from {O}%s{R} wireless interface{W}' %interface)
                    continue
            

    @staticmethod
    def get_network_info_cont(ssid):  
        dict_cont = {}
        
        # Get WiFi properties using nmcli
        p = Process('nmcli ' + '-p ' + 'connection ' + 'show ' + ssid)
        lines = p.stdout().split('\n')
        
        for line in lines:    
            if '802-11-wireless-security.key-mgmt' in line:
                security = line.split(':')[1].strip()
                dict_cont['Security Type'] = security
                
            if 'IP4.ADDRESS[1]' in line:
                Properties.local_ipv4_add = line.split(':')[1].strip()
                dict_cont['Public IPv4'] = Properties.pub_ipv4_add
                dict_cont['Private IPv4'] = Properties.local_ipv4_add

            if 'IP4.DNS[1]' in line:
                ipv4_dns_1 = line.split(':')[1].strip()
                dict_cont['IPv4 DNS[1]'] = ipv4_dns_1
                
            if 'IP4.DOMAIN[1]' in line:
                ipv4_dom_1 = line.split(':')[1].strip()
                dict_cont['IPv4 Domain[1]'] = ipv4_dom_1
                
            if 'IP4.DOMAIN[2]' in line:
                ipv4_dom_2 = line.split(':')[1].strip()
                dict_cont['IPv4 Domain[2]'] = ipv4_dom_2
                
            if 'IP6.ADDRESS[1]' in line:
                if Properties.pub_ipv6_add == 'N/A':
                    ipv6_add_1 = line.split()[1]
                    dict_cont['Public IPv6'] = ipv6_add_1
                else:
                    dict_cont['Public IPv6'] = Properties.pub_ipv6_add
                
            if 'IP6.ADDRESS[2]' in line:
                ipv6_add_2 = line.split()[1]
                dict_cont['Link-local IPv6'] = ipv6_add_2
                
            if 'IP6.DNS[1]' in line:
                ipv6_dns_1 = line.split()[1]
                dict_cont['IPv6 DNS[1]'] = ipv6_dns_1
                
            if 'IP6.DNS[2]' in line:
                ipv6_dns_2 = line.split()[1]
                dict_cont['IPv6 DNS[2]'] = ipv6_dns_2
                
        return dict_cont
    
    @staticmethod
    def discovery(ip_addr):
        Properties.host = 0
        network = ipaddress.IPv4Network(ip_addr, strict=False)
        
        # run the nmap -sn command to discover devices on the network
        Properties.network_ip = (f"{network.network_address}/{network.prefixlen}") 
        cmd = ['sudo', 'nmap', '-sn', Properties.network_ip]
        p = Process(cmd)

        # parse the output to extract the list of devices
        devices = []
        for line in p.stdout().splitlines():
            
            if 'Nmap scan report for' in line:
                info = line.split()
                ip = info[-1].strip('(').strip(')')
                name = info[-2] if len(info) > 5 else 'None'
                devices.append(ip)
                devices.append(name)
                Properties.host += 1
                
            elif 'MAC Address:' in line:
                info = line.split()
                mac = info[2]
                manufacturer = (''.join(info[3:len(info)])).strip('(').strip(')')
                devices.append(mac)
                devices.append(manufacturer)
                
        return devices

    @staticmethod
    def valid_ip(address): # Check if IP address is valid
        try: 
            socket.inet_aton(address)
            return True
        except:
            return False
