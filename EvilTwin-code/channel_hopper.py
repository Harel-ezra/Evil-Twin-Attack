from time import sleep
from sys import argv
from os import system

def main(iface, timeout):
    """
    This file runs on a background proccess and manages the channel hopping.

    :param str iface: interface to work on
    """

    # while parent's proccess alive and not shutted menually
    while True:

        # this 3 channels are the only channels which has no overlapping. each other channel can be caught on-the-way
        for i in range(1,13):
            system(f'sudo iwconfig {iface} channel {i}')

            # sleeping for better channel sniffing without hopping constantly
            sleep(int(timeout) / 12 / 2)



if __name__ == "__main__":
    main(argv[1], argv[2])