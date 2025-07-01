import os
import subprocess
import socket

env = os.environ.copy()

def run_command(command):
    result = subprocess.run(command, env=env, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Command '{command}' failed with error: {result.stderr.strip()}")
    return result.stdout.strip()

def is_device_reachable(ip, port=22, timeout=3):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False

def ip_exists_on_interface(interface, ip):
    try:
        result = subprocess.run(
            ["ip", "addr", "show", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return ip in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Failed to get IPs for {interface}: {e.stderr}")
        return False

print("Starting Voyant Client Basic Example.\nBegining automatic setup of network interface for LiDAR...")

# Collect ip address information
print("Collecting available network interfaces...")
ip_addrs = run_command('ip addr').split('\n')

# Parse the output to find interface names
print("Parsing available network interfaces...")
interface_names = []
for addr in ip_addrs:
    if addr[0].isnumeric():
        interface_name = addr.replace(" ", "").split(":")[1]
        interface_names.append(interface_name)
print("Available Network Interfaces:")
for name in interface_names:
    print(f"   {interface_names.index(name) + 1}. {name}")
selected_interface = input("Select network interface of LiDAR by number: ")

selected_interface = interface_names[int(selected_interface) - 1]
print(f"Selected Interface: {selected_interface}")
# if not selected_interface.isnumeric() or int(selected_interface) < 1 or int(selected_interface

if ip_exists_on_interface(selected_interface, "192.168.20.100/24"):
    print("Address already assigned to the interface. Skipping IP address assignment.")
else:
    print("Assigning IP address")
    run_command(f"ip addr add 192.168.20.100/24 dev {selected_interface}")
    run_command(f"ip link set {selected_interface} up")

print(f"Network interface {selected_interface} configured with IP address. Testing connection...")
if not is_device_reachable("192.168.20.20"):
    print("Error: LiDAR device is not reachable. Please check the connection and try again.")
else:
    print("Connection to LiDAR device established successfully.")


print("Starting Voyant Client...\nWould you like to build Docker Container (only required if never built before or if chages have been made since last build)? (y/n): ")
build_container = input().strip().lower()
if build_container == 'y':
    print("Building Docker container...")
    run_command("docker build -t voyant-sdk-container -f docker/Dockerfile .")
    print("Docker container built successfully.")
else:
    print("Skipping Docker container build.")

print("Running Docker container...")
try: 
    subprocess.run([
        "gnome-terminal",
        "--",
        "bash", "-c",
        "docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash; exec bash"
    ])
except Exception as e:
    run_command("docker stop voyant-sdk-container")
    run_command("docker rm voyant-sdk-container")
    print("Sussy baka")
    subprocess.run([
        "gnome-terminal",
        "--",
        "bash", "-c",
        "docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash; exec bash"
    ])