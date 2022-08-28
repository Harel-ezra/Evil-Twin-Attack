from scapy.all import *
import settings

def packet_handler(packet: scapy.packet):
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
                    print('{}{}\t\t{}\t\t{:<10}'.format(f'{len(settings.ap_list) - 1}: ',f'MAC: {beacon_addr}', f'Channel: {beacon_channel}', f'SSID: {beacon_name}'))

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
                    settings.client_list[packet.addr1.upper()].append(packet.addr2.upper())


                

def run():
    """
    This function basically interacts with the user and calling scapy.sniff() with the callback function written above.
    It recieves the needed parameters from th global variables file 'settings.py'
    """
    print(f'************** Sniffing {settings.monitor} for {settings.time_out} seconds **************\n')

    # scapy's sniff method with packet_handler as the callback function
    sniff(iface = settings.monitor, prn = packet_handler, timeout=settings.time_out)

    print(f'\n**************** Finished sniffing {settings.monitor} *****************')


