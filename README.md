# Wi-Fi Password Cracking and Crafting tool (WP2C)
WP2C is a command-line tool designed to crack and craft Wi-Fi passwords. It allows users to exploit the WPA Wi-Fi encryption flaw by capturing 4-way handshakes and performing dictionary attacks to crack the password from the captured handshake packets. 

## Features

### Initialise WP2C
Initialising WP2C means starting the program and preparing it for use. This process involves setting up the configuration variables and functions for WP2C and checks necessary Python modules and installs them if not found.

### Capture WPA 4-way Handshakes
WP2C can capture WPA 4-way handshakes from Wi-Fi networks. A 4-way handshake is a process that occurs when a client connects to a Wi-Fi network protected by WPA encryption.

### Dictionary Attack
WP2C can perform a dictionary attack to crack the password from the captured handshake packets. It uses a list of possible passwords in a dictionary file to try to guess the correct password.

### Password Strength Checking
WP2C can check the strength of a Wi-Fi password. It analyzes the password to determine if it meets commonly accepted password strength criteria, such as minimum length, complexity, and use of special characters.

### Password Generation
WP2C can generate new Wi-Fi passwords. It creates a random password based on specified parameters, such as length and user desired word.

### Wi-Fi Properties and Devices Discovery
WP2C can display Wi-Fi properties, such as SSID, channel, signal strength, and encryption type. It can also list devices connected to the Wi-Fi network, including their MAC addresses and IP addresses.

### Wi-Fi Speed Test
WP2C can test the Wi-Fi upload and download speed and ping. It provides an easy way to verify the Wi-Fi network's performance.

### Report Generation
WP2C can generate a report after cracking a Wi-Fi. The report includes the network's SSID, MAC address, encryption type, password and other relevant information.


# Usage
## Prerequisites
1. Linux Operating System (tested on Kali Linux 2022.4 release version)
2. A wireless network adapter that supports monitor mode (check out [list for compatible adapters](https://deviwiki.com/wiki/List_of_Wireless_Adapters_That_Support_Monitor_Mode_and_Packet_Injection))

## Installation
Clone the WP2C repository from GitHub:

```
git clone https://github.com/J430N/WP2C.git
```

## Adding New Wordlist
Save the new wordlist in the [wordlist](https://github.com/J430N/WP2C/tree/master/wordlist) folder.
**Important: Only plain text files (i.e., files with a `.txt` extension) are allowed to save in the `wordlist` folder. Any other file types will be ignored by WP2C.**

## Attack WPA encrypted Wi-Fi
Change to the WP2C directory:
```
cd WP2C
```
Run the WP2C tool:
```
sudo python wp2c.py
```

## Help
```
sudo python wp2c.py -h
```

## Verbose
```
sudo python wp2c.py -v
```

## Wi-Fi Properties and Devices Discovery
```
sudo python wp2c.py --properties
```

## Wi-Fi Speed Test
```
sudo python wp2c.py --speed
```

## Check Password Strength
```
sudo python wp2c.py --password
```

## Generate New Password
```
sudo python wp2c.py --generate
```

## Capture New Handshake (Ignore Existing Handshake)
```
sudo python wp2c.py --new
```

## Cracked Wi-Fi History
```
sudo python wp2c.py --history
```

## Check Handshake File
```
sudo python wp2c.py --check
```
## Crack Captured Handshake
```
sudo python wp2c.py --crack
```

# Disclaimer
This tool is intended for educational and research purposes only. The authors are not responsible for any misuse or damage caused by this tool. Use at your own risk.
