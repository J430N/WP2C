#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
from .iw import Iw
from util.color import Color
from config import Configuration


class Properties:
    """Get properties of WiFi networks."""
    dict_list = []
    
    @classmethod
    def run(cls):
        
        Configuration.initialize(False)
        
        if not cls.get_network_info() is False:
            Color.pl('\n{O}---------- Network Information ----------')
            for dict in Properties.dict_list:
                for key, value in dict.items():
                    Color.p('{P}%s: ' % str(key).ljust(17))
                    Color.pl('{W}%s' % str(value).ljust(42))
        else:
            Color.pl('{!} {R}Error: {O}WP2C{R} could not find any network interfaces{W}')

                    
    @classmethod
    def get_network_info(cls):
        
        interfaces = Iw.get_interfaces()
        
        if len(interfaces) == 0:
            return False
        else:
            # First row: columns
            Color.p('   NUM')
            Color.pl('  Network Interface')
            Color.p('   ---')
            Color.pl('  -----------------')
            
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
                
                dict = {} # Create a dict for each interface
                dict['Network Interface'] = interface        

                # Get WiFi properties using iwconfig
                output = subprocess.check_output(['iwconfig', interface])
                lines = output.decode().split('\n')

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
                        dict.update(cls.get_network_info_cont(ssid))
                    
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

    @classmethod
    def get_network_info_cont(cls, ssid):  
        dict_cont = {}
            
        # Get WiFi properties using nmcli
        output = subprocess.check_output(['nmcli', '-p', 'connection', 'show', ssid]) #Wifi name from the network interface
        lines = output.decode().split('\n')

        for line in lines:
            if '802-11-wireless-security.key-mgmt' in line:
                security = line.split(':')[1].strip()
                dict_cont['Security Type'] = security
                
            if 'IP4.ADDRESS[1]' in line:
                ipv4_add_1 = line.split(':')[1].strip()
                dict_cont['IPv4 Address[1]'] = ipv4_add_1
                
            if 'IP4.ADDRESS[2]' in line:
                ipv4_add_2 = line.split(':')[1].strip()
                dict_cont['IPv4 Address[2]'] = ipv4_add_2
                
            if 'IP4.DNS[1]' in line:
                ipv4_dns_1 = line.split(':')[1].strip()
                dict_cont['IPv4 DNS[1]'] = ipv4_dns_1
                
            if 'IP4.DNS[2]' in line:
                ipv4_dns_2 = line.split(':')[1].strip()
                dict_cont['IPv4 DNS[2]'] = ipv4_dns_2
                
            if 'IP4.DOMAIN[1]' in line:
                ipv4_dom_1 = line.split(':')[1].strip()
                dict_cont['IPv4 Domain[1]'] = ipv4_dom_1
                
            if 'IP4.DOMAIN[2]' in line:
                ipv4_dom_2 = line.split(':')[1].strip()
                dict_cont['IPv4 Domain[2]'] = ipv4_dom_2
                
            if 'IP6.ADDRESS[1]' in line:
                ipv6_add_1 = line.split()[1]
                dict_cont['IPv6 Address[1]'] = ipv6_add_1
                
            if 'IP6.ADDRESS[2]' in line:
                ipv6_add_2 = line.split()[1]
                dict_cont['IPv6 Address[2]'] = ipv6_add_2
                
            if 'IP6.DNS[1]' in line:
                ipv6_dns_1 = line.split()[1]
                dict_cont['IPv6 DNS[1]'] = ipv6_dns_1
                
            if 'IP6.DNS[2]' in line:
                ipv6_dns_2 = line.split()[1]
                dict_cont['IPv6 DNS[2]'] = ipv6_dns_2
            
        return dict_cont

# Connect to Wifi after cracked
# wifi connect (B)SSID [password password] [wep-key-type {key | phrase}] [ifname ifname]
#        [bssid BSSID] [name name] [private {yes | no}] [hidden {yes | no}]

#Connect this to a arguments in args.py