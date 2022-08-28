import settings


def mode_switcher(mode, iface = None, verbose = 1):
    """
    This function handles the mode-changing of an interface.
    Using os.system() for system calls (with sudo)
    Arguments = 
        iface: string - mainly for testings. if not given using the global iface from settings.py
        mode : string - 'monitor' or 'managed'
    """
    if verbose: print(f'\nswitching {iface or settings.monitor} to {mode} mode...\n')
    try:
        settings.system_operation(f'sudo ifconfig {iface or settings.monitor} down')
        settings.system_operation(f'sudo iwconfig {iface or settings.monitor} mode {mode}')
        settings.system_operation(f'sudo ifconfig {iface or settings.monitor} up')

    except PermissionError:
        print(f"Permission denied for changing {iface or settings.monitor}'s mode to {mode}. Please make sure you run the program with 'sudo'")
    except:
        print(f'Could not change {iface or settings.monitor} mode to {mode}')
