import socket # for connecting
from colorama import init, Fore
# some colors
init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX

max = int(input("Enter the maximum port number to scan (default 1024): "))
if max < 1:
    print("Invalid port number. Using default value.")

def is_port_open(host, port):
    """determine whether `host` has the `port` open"""
    # creates a new socket
    s = socket.socket()
    try:
    # tries to connect to host using that port
        s.connect((host, port))
    # make timeout if you want it a little faster ( less accuracy )
        s.settimeout(0.2)
    except:
    # cannot connect, port is closed
    # return false
        return False
    else:
    # the connection was established, port is open!
        return True

host = input("Enter the host:")
# iterate over ports, from 1 to 1024
for port in range(1, max):
    if is_port_open(host, port):
        print(f"{GREEN}[+] {host}:{port} is open {RESET}")
    else:
        print(f"{GRAY}[!] {host}:{port} is closed {RESET}", end="\r")