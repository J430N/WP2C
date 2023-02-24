import subprocess


def get_network_info():
    
    ssid = 'C-20-8' # change 
    device = 'wlan0' # change 
    result = {}

    try:
        # Get WiFi properties using nmcli
        output = subprocess.check_output(['nmcli', '-p', 'connection', 'show', ssid])
        lines = output.decode().split('\n')
        
        for line in lines:
            if 'connection.id' in line:
                ssid = line.split(':')[1].strip()
                result['SSID'] = ssid
            elif '802-11-wireless.seen-bssids' in line:
                mac = line.split()[1]
                result['MAC Address'] = mac
            elif '802-11-wireless-security.key-mgmt' in line:
                security = line.split(':')[1].strip()
                result['Security Type'] = security
            # elif '802-11-wireless-security.key-mgmt' in line:
            #     manufacturer = line.split(':')[1].strip()
            #     result['Manufacturer'] = manufacturer #Check target to pass the manufacturer name
            elif 'IP4.ADDRESS[1]' in line:
                ipv4_add = line.split(':')[1].strip()
                result['IPv4 Address'] = ipv4_add
            elif 'IP4.DNS[1]' in line:
                ipv4_dns = line.split(':')[1].strip()
                result['IPv4 DNS'] = ipv4_dns
            elif 'IP4.DOMAIN[1]' in line:
                ipv4_dom = line.split(':')[1].strip()
                result['IPv4 Domain'] = ipv4_dom
            elif 'IP6.ADDRESS[1]' in line:
                ipv6_add = line.split()[1]
                result['IPv6 Address'] = ipv6_add
            elif 'IP6.DNS[1]' in line:
                ipv6_dns = line.split()[1]
                result['IPv6 DNS'] = ipv6_dns
                
        # Get WiFi properties using iwconfig
        output = subprocess.check_output(['iwconfig', device])
        lines = output.decode().split('\n')
        for line in lines:
            if '802.11' in line:
                band = line.split()[2]
                result['Network Band'] = band
            elif 'Frequency' in line:
                frequency = line.split('Frequency:')[1].split()[0]
                result['Frequency'] = frequency + ' Ghz'
            elif 'Link Quality' in line:
                quality = line.split('Link Quality=')[1].split(' ')[0]
                result['Link Quality'] = quality
            elif 'Signal level' in line:
                signal_level = line.split('Signal level=')[1].split(' ')[0]
                result['Signal Level'] = signal_level
              
#Arrange them neatly  
#Fix the last one to display       

    except subprocess.CalledProcessError:
        pass

    return result

network_info = get_network_info()

print('--- Network Information ---')
for key, value in network_info.items():
    print(f'{key}: {value}')

# Connect to Wifi after cracked
# wifi connect (B)SSID [password password] [wep-key-type {key | phrase}] [ifname ifname]
#        [bssid BSSID] [name name] [private {yes | no}] [hidden {yes | no}]
