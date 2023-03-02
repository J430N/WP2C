#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .iw import Iw
from util.color import Color
from config import Configuration
import subprocess
import ipaddress
import socket


class Properties:
    """Get properties of WiFi networks."""
    Configuration.initialize(False)
 
    dict_list = []
    ipv4_add_1 = None
    ipv4_add_2 = None
    
    @classmethod
    def run(cls):

        if not Properties.get_network_info() is False and len(Properties.dict_list) > 0:
            Color.pl('\n{W} ------------------{G} Wi-Fi Properties {W}------------------')
            for dict in cls.dict_list:
                for key, value in dict.items():
                    Color.p('{+} {W}%s: ' % str(key).ljust(19))
                    Color.pl('{C}%s' % str(value))

                # print out the infomations of the founded devices and the summary               
                if Properties.ipv4_add_1 is not None:
                    Color.pl('\n{+} {W}Discovering devices on the {C}%s {W}network...' % Properties.dict_list[0]['SSID'])                
                    Color.pl('\n{W} ------------------{G} Devices Connected to %s {W}------------------' % Properties.dict_list[0]['SSID'])
                    attribute = ['Name', 'MAC Address', 'Manufacturer']
                    count = 0
                        
                    for element in Properties.discovery(Properties.ipv4_add_1):
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
                
                if Properties.ipv4_add_2 is not None:
                    attribute = ['Name', 'MAC Address', 'Manufacturer']
                    count = 0
                        
                    for element in Properties.discovery(Properties.ipv4_add_2):
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
                    Color.pl('{C}Found {O}%d{C} devices on the {W}' % Properties.host + Properties.network_ip + '{C} network{W}')
            Color.pl('{W}------------------ {G}Thank You {W}------------------')    
                    
        else:
            Color.pl('{!} {R}Error: {O}WP2C{R} could not find any wireless interfaces{W}')

                    
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
        output = subprocess.check_output(['nmcli', '-p', 'connection', 'show', ssid]) #Wifi name from the network interface
        lines = output.decode().split('\n')

        for line in lines:
            if '802-11-wireless-security.key-mgmt' in line:
                security = line.split(':')[1].strip()
                dict_cont['Security Type'] = security
                
            if 'IP4.ADDRESS[1]' in line:
                Properties.ipv4_add_1 = line.split(':')[1].strip()
                dict_cont['IPv4 Address[1]'] = Properties.ipv4_add_1
                
            if 'IP4.ADDRESS[2]' in line:
                Properties.ipv4_add_2 = line.split(':')[1].strip()
                dict_cont['IPv4 Address[2]'] = Properties.ipv4_add_2

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
    
    @staticmethod
    def discovery(ip_addr):
        Properties.host = 0
        network = ipaddress.IPv4Network(ip_addr, strict=False)
        
        # run the nmap -sn command to discover devices on the network
        Properties.network_ip = (f"{network.network_address}/{network.prefixlen}") 
        cmd = ['sudo', 'nmap', '-sn', Properties.network_ip]
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # parse the output to extract the list of devices
        devices = []
        for line in output.stdout.decode().splitlines():
            
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
