import argparse
import socket # for connecting
from colorama import init, Fore
from threading import Thread, Lock
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# some colors
init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX
# number of threads, feel free to tune this parameter as you wish
N_THREADS = 200
# thread queue
q = Queue()

print_lock = Lock()


def scan_open_ports(host, start_port, end_port, timeout=0.5, max_workers=200):
    """Return a sorted list with open ports in the given range."""
    if start_port > end_port:
        start_port, end_port = end_port, start_port

    ports = list(range(start_port, end_port + 1))
    open_ports = []

    def is_open(port):
        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return port
        except OSError:
            return None
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(is_open, p) for p in ports]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                open_ports.append(result)

    return sorted(open_ports)


def port_scan(host, port):
    """Scan one TCP port on the given host."""
    try:
        s = socket.socket()
        s.settimeout(0.5)
        s.connect((host, port))
    except:
        with print_lock:
            print(f"{GRAY}{host:15}:{port:5} is closed {RESET}", end='\r')
    else:
        with print_lock:
            print(f"{GREEN}{host:15}:{port:5} is open {RESET}")
    finally:
        s.close()

def scan_thread(host):
    global q
    while True:
        # get the port number from the queue
        worker = q.get()
        # scan that port number
        port_scan(host, worker)
        # tells the queue that the scanning for that port
        # is done
        q.task_done()


def main(host, ports):
    global q
    for _ in range(N_THREADS):
        # for each thread, start it
        t = Thread(target=scan_thread, args=(host,))
        # when we set daemon to true, that thread will end when the main thread ends
        t.daemon = True
        # start the daemon thread
        t.start()

    for worker in ports:
        # for each port, put that port into the queue
        # to start scanning
        q.put(worker)

    # wait the threads (port scanners) to finish
    q.join()

if __name__ == "__main__":
    # parse some parameters passed
    parser = argparse.ArgumentParser(description="Fast port scanner")
    parser.add_argument("host", nargs="?", help="Host to scan.")
    parser.add_argument("--ports", "-p", dest="port_range",
    default="1-65535", help="Port range to scan, default is 1-65535 (all ports)")
    args = parser.parse_args()

    host = args.host or input("Host to scan: ").strip()
    if not host:
        print("No host provided.")
        raise SystemExit(1)

    port_range = args.port_range
    start_port, end_port = port_range.split("-")
    start_port, end_port = int(start_port), int(end_port)
    ports = [p for p in range(start_port, end_port + 1)]
    main(host, ports)
