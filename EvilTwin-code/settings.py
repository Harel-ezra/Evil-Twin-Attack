def init():
    """
    This file holds all of program's shared variables.
    All variables here are global and can be accessed from all files.
    """

    # Access Points list holds each AP as: {AP's name: (AP's uppercase MAC, AP's channel)}
    global ap_list

    # timeout for the sniffing proccess - default 60
    global time_out

    # holds Interface's name for handling all proccesses reffering to the same one.
    global monitor

    # Connected interface to forward all requests through
    global internet

    global hosting

    # holds ap's name for faking it.
    global ap_name

    # Client list holds each AP's clients as: {AP's MAC: [list of Clients MAC addresses]}
    global client_list
    
    # For defence - counting deauth pkts
    global pkt_count

    global target

    global target_mac

    global blacklist

    global deauth

    ap_list = {}
    client_list = {}
    time_out = 60
    monitor = ""
    internet = ""
    hosting = ""
    ap_name = ""
    pkt_count = 0
    target = ""
    target_mac = ""
    blacklist = {}
