import subprocess
from .iw import Iw
from util.color import Color
from config import Configuration

dict_list = []
Configuration.initialize(load_interface=False) #See condition to change

def get_network_info():
    
    interfaces = Iw.get_interfaces(mode='managed') # change 
    
    if len(interfaces) == 0:
        return False
    else:
        try:
            for interface in interfaces:
                dict = interface
                dict = {}           
                
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
                        dict.update(get_network_info_cont(ssid))
                    
                    if 'Access Point' in line:
                        mac = line.split('Access Point:')[1]
                        dict['MAC Address'] = mac
                        
                        oui = ''.join(mac.split(':')[:3]).strip() # Use oui in MAC address to find manufacturer                       
                        manufacturer = Configuration.manufacturers.get(oui, "")
                        dict['Manufacturer'] = manufacturer 
                        
                    if 'Link Quality' in line:
                        quality = line.split('Link Quality=')[1].split()[0]
                        dict['Link Quality'] = quality
                        
                    if 'Signal level' in line:
                        signal_level = line.split('Signal level=')[1].split()[0]
                        dict['Signal Level'] = signal_level
                          
                dict_list.append(dict) # Add dict to list     
            return dict_list
            
        except subprocess.CalledProcessError:
            return False

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
                
network_info = get_network_info()

if network_info == False:
    Color.pl('{!} {R}Error: {O}WP2C{R} could not find any network interfaces{W}')
else:
    print('--- Network Information ---')
    for dict in dict_list:
        for key, value in dict.items():
            print(f'{key}: {value}')

# Connect to Wifi after cracked
# wifi connect (B)SSID [password password] [wep-key-type {key | phrase}] [ifname ifname]
#        [bssid BSSID] [name name] [private {yes | no}] [hidden {yes | no}]

#Connect this to a arguments in args.py
