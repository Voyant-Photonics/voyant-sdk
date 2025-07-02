import os
import subprocess
import socket
import logging

# Set up terminal envirment and logging
env = os.environ.copy()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function definitions
def run_command(command, capture=False): # Runs a shell command and returns the output
    result = subprocess.run(command, env=env, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        raise Exception(f"Command '{command}' failed with error: {result.stderr.strip()}")
    if capture:
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
        logging.error(f"Failed to get IPs for {interface}: {e.stderr}")
        return False

def get_lidar_interface_name(): # Function to get the interface name for lidar with user input
    # Parse the output to isolate interface names
    interface_names = []
    for network_interface in network_interfaces:
        if network_interface[0].isnumeric():
            interface_name = network_interface.replace(" ", "").split(":")[1]
            interface_names.append(interface_name)

    # Print available network interfaces and prompt user for selection
    logging.info("===-Available Network Interfaces-===")
    ethernet_extensions = ["eth", "eno", "enx"]
    for interface_name in interface_names:
        if any(ext in interface_name for ext in ethernet_extensions):
            logging.info(f"   {interface_names.index(interface_name) + 1}. {interface_name} \033[32m<- likely lidar\033[0m")
        else:
            logging.info(f"   {interface_names.index(interface_name) + 1}. {interface_name}")

    selected_interface = input("Please enter number to select network interface of LiDAR: ")

    if selected_interface.isdigit() and int(selected_interface) > 0 and int(selected_interface) <= len(interface_names):
        selected_interface = interface_names[int(selected_interface) - 1]
        logging.info(f"Selected network interface: {selected_interface}")
        return selected_interface
    else:
        logging.warning("Invalid selection. Please try again.")
        return get_lidar_interface_name()

# Start the Automated Voyant Client Setup
logging.info("==========-Starting Voyant Client Automated Setup-==========")

# Collect all network interfaces
network_interfaces = run_command('ip addr', capture=True).split('\n')

# Check if any network interfaces were found
if len(network_interfaces) == 0:
    logging.error("No network interfaces found. Make sure your lidar is connected via ethernet to this device and powered on. Once done, rerun this script. Exiting setup.")
    exit(1)

selected_interface = get_lidar_interface_name()

# Link up with the selected interface. Skip prosses if the interface is already liked with
if ip_exists_on_interface(selected_interface, "192.168.20.100/24"):
    logging.info("Address already assigned to lidar interface. Skipping IP address assignment.")
else:
    logging.info("Assigning IP address to lidar interface.")
    run_command(f"ip addr add 192.168.20.100/24 dev {selected_interface}")
    run_command(f"ip link set {selected_interface} up")

# Verify connection
logging.info(f"Network lidar interface {selected_interface} configured with IP address. Testing connection.")
if not is_device_reachable("192.168.20.20"):
    logging.error("Lidar device is unresponsive. Please check the connection and ensure the device is powered on, then rerun this script. Exiting setup.")
    exit(1)
else:
    logging.info("Connection to lidar device verified successfully.")

# Build Docker container if needed. Need determined by user input
logging.info("===-Starting Voyant Client-===\nWould you like to build Docker Container (only required if never built before or if changes have been made since last build)? (y/n): ")
build_container = input().strip().lower()
if build_container == 'y':
    logging.info("Building Docker container. This will most likely take a while. I would recommend having a really good book on hand.")
    run_command("docker build --no-cache -t voyant-sdk-container -f docker/Dockerfile .")
    logging.info("Docker container built successfully.")
else:
    logging.info("Skipping Docker container build.")

# Run Docker container
logging.info("Running Docker container. This will open a new terminal window with the container running. You can now use the Voyant SDK with all of the api controls listed in to documentation (https://voyant-photonics.github.io/) inside the container.")
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
    subprocess.run([
        "gnome-terminal",
        "--",
        "bash", "-c",
        "docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash; exec bash"
    ])
logging.info("Voyant Client setup completed successfully. You can now use the Voyant SDK inside the Docker container. For more information, refer to the documentation at https://voyant-photonics.github.io/.")