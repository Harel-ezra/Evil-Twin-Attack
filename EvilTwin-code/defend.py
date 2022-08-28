import signal
import subprocess
import sys
import sniffer
from time import sleep
from scapy.all import RadioTap, Dot11, Dot11Deauth, Dot11Beacon, sniff, sendp, packet
from netifaces import interfaces, ifaddresses
from mode_switcher import mode_switcher
import settings

def terminate():
    """
    Safe termination - changing inteface's mode back to managed.
    """

    # read 'mode_switcher.py' documentation for more information
    mode_switcher('managed')
    print('Terminating Program...')
    exit(0)
    

def signal_handler(sig_num=None, frame=None):
    """
    Signal handler for CTRL+C
    """
    
    # for multiple CTRL+C pressing
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print('\nCTRL+C Caught, do you want to exit the program? [Y/N]')
    ans = input()
    print("")

    # if user enters y/yes - terminate program
    if ans.lower() == 'y' or ans.lower() == 'yes':
        terminate()

def packet_handler(packet: packet):
    if packet.haslayer(Dot11Beacon):
        name = packet.info.decode('utf-8')
        if name and name not in settings.ap_list and packet.addr2.upper() not in settings.blacklist.keys():
            print(f"Potential Risk: '{name}' : {packet.addr2.upper()}")
            settings.blacklist[packet.addr2.upper()] = name
    elif packet.haslayer(Dot11Deauth):
        
        if packet.addr1.upper().strip() == settings.target_mac or packet.addr2.upper().strip() == settings.target_mac or packet.addr3.upper().strip() == settings.target_mac :
            settings.pkt_count += 1 
            if settings.pkt_count > 20:
                if packet.addr1.upper().strip() == settings.target_mac and (packet.addr1.upper() in settings.blacklist.keys() or len(settings.blacklist) == 0):

                    ddos_attack(packet.addr2)
                else:
                    ddos_attack(packet.addr1)

                terminate()

def ddos_attack(mac_addr):
    print('ABNORMAL ACTIVITY DISCOVERED!!!!')
    pkt_ap = RadioTap()/Dot11(addr1 = mac_addr.lower(), addr2 = '00:00:00:00:00:00', addr3 = mac_addr.lower())/Dot11Deauth(reason=7)
    pkt_client = RadioTap()/Dot11(addr1 = settings.target_mac.lower(), addr2 = mac_addr.lower(), addr3 = mac_addr.lower())/Dot11Deauth(reason=7)
    print(f'Trying to take down the attacker ({mac_addr})...')
    for i in 1000:
        sendp(pkt_ap, iface=settings.iface, count=10)
        sendp(pkt_client, iface=settings.iface, count = 10)

def main():
    print('\n------------- EvilTwin Defence -------------\n')
    signal.signal(signal.SIGINT, signal_handler)
    settings.init()

    print('Availible Intefaces:')
    for i, j in enumerate(interfaces()):
        print(f' {i}: {j}')

    # assigning Interface's name
    iface_input = input(
        f"\nChoose an interface to sniff: ").strip()
    while (not iface_input.isnumeric()) and settings.iface not in interfaces():
        print("Not a valid index! see listed interfaces' indexing")
        iface_input = input(
            f"\nChoose an interface to sniff: ").strip()

    settings.iface = interfaces()[int(iface_input)]

    to = input('OPTIONAL: Timeout for sniffing ( default is 60s ): ').strip()
    if to.isnumeric():
        # assigning time-out for sniffing interface if given - 60 seconds defaultwaaaaaa211111
        settings.time_out = int(to)

    # switching interface's mode to monitor
    mode_switcher('monitor')

    # some basic UX communication
    print(f'\nSniffing traffic on {settings.iface}...\n')
    print('*****************************************************************')
    print('*                                                               *')
    print('*\tTo stop program from running press CTRL+C at any time!\t*')
    print('*                                                               *')
    print('*****************************************************************')

    # The next line opens a new process as a sub-proccess with a different session - for asynchronic run
    hopper_id = subprocess.Popen(
        [sys.executable, 'channel_hopper.py', settings.iface, str(settings.time_out)], start_new_session=True).pid

    # read 'sniff.py' documentation for more information
    sniffer.run()

    # stop channel hopping, not neccessary any more
    settings.system_operation(f'sudo kill -9 {hopper_id}')

    # selecting Access Point to attack
    flag = False
    while not flag:
        settings.ap_name = input(
            "Please name one of the Access Points above to scan it's clients: ").strip()

        if settings.ap_name not in settings.ap_list:
            print(
                f"\n!!! {settings.ap_name} is not listed. Please provide a listed name of the above !!!\n")

        else:
            ap_mac = settings.ap_list[settings.ap_name][0]
            flag = True

    # printing Access Point's clients
    try:
        1 / len(settings.client_list[ap_mac])
        print(f"\n{settings.ap_name}'s connected clients are: ")
        for i, v in enumerate(settings.client_list[ap_mac]):
            print(f'{i}:\t{v}')
        print('')
    except:
        print(f'\n{settings.ap_name} has no connected clients!\n')
        flag = False

    # selecting a client to attack
    while flag:

        target = input("Choose a client to defend (by it's index): ").strip()
        if target.isnumeric():
            target_num = int(target)
            if target_num >= 0 and target_num < len(settings.client_list[ap_mac]):
                settings.target_mac = settings.client_list[ap_mac][target_num]
                flag = False
                
            else:
                print(f'\n{target_num} is not a valid index. Try again\n')
        else:
            print(f"\n'{target}' is not a valid input. Try again\n")

    print('checking for vulnerabilities...\n')
    mode_switcher('monitor', verbose=0)
    while True:
        settings.pkt_count = 0
        sniff(iface = settings.iface, prn = packet_handler, timeout = 10)

    

    

    

if __name__ == '__main__':
    main()