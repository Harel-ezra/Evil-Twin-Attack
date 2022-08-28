from os import getuid
import settings
if __name__== '__main__':

    print("------------- Checking for requirements -------------")
    settings.system_operation('bash ./init.sh')
    print("------------- All requirements satisfied -------------")
    settings.system_operation('clear')

    print("------------- EvilTwin Attack and Defence -------------")
    # checking for SuperUser permission
    if getuid():
        print('ERROR!\nThis program can only run in SUDO.\nPlease run the program again with "sudo" prefix.\nTerminating...')
        exit(1)
    choice = input(f'Please choose whether you wnat to attack or defend:\n1: Attack\n2: Defend\nChoice: ')
    while not choice.isnumeric() or int(choice) > 2 or int(choice) < 1:
        choice = input('Invalid Input! please insert: \n1 - to attack\n2 - to defend\nchoice: ')
    choice = int(choice)
    
    settings.system_operation('clear')
    if choice == 1:
        settings.system_operation('python3 attack.py')
    else:
        settings.system_operation('python3 defend.py')
