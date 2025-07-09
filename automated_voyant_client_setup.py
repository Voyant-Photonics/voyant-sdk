import os
import subprocess
import socket
import logging
import sys
import argparse
import signal

parser = argparse.ArgumentParser(description="Automatic Voyant Client Setup Script & Voyant Client API Interface.")
parser.add_argument("--setup", type=str, default='true', help=" Determines whether or not to run the script in setup mode. If false, the script will run in Voyant Client API Interface mode.")
parser.add_argument("--data", type=list, default = [], help="Data to be passed to the Voyant Client API Interface. This is made by the program is seup mode, and should not be made manually.")
args = parser.parse_args()

# Set up terminal envirment and logging
env = os.environ.copy()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Utility functions
def run_command(command, capture=False): # Runs a shell command and returns the output if capture is True
    result = subprocess.run(command, env=env, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        raise Exception(f"Command '{command}' failed with error: {result.stderr}")
    if capture:
        return result.stdout

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

def render_menu(options, prompt="Please input response: ", title = None, refresh=False, cancel = False, note = None): # Function to print a menu and get user input
    # Print menu title
    if title != None:
        logging.info(f"=====-{title}-=====")
    if note != None:
        logging.info(f"Note: {note}")
    # Print options as numbered list
    logging.info("===-Available Options-⌄")
    #Add a "Refresh" option if requested
    if refresh and "Refresh" not in options:
        options.append("Refresh")
    if cancel and "Cancel" not in options:
        options.append("Cancel")
    # Print each option with its index
    for i, option in enumerate(options):
        if type(option) == list:
            option = " ".join(option)
            options[i] = options[i][0]
        logging.info(f"    {i + 1}. {option}")
    # Prompt user for input
    choice = input(prompt).strip()
    # Validate input and return selected option
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1]
    elif choice.lower() in [option.lower() for option in options]:
        return options[[option.lower() for option in options].index(choice.lower())]
    else:
        logging.warning("Invalid selection. Please try again.")
        return render_menu(options, prompt, title, refresh)

def render_info(info, title=None):
    # Print information message
    if title:
        logging.info(f"=====-{title}-=====")
    for label in info.keys():
        if info[label] == "False" or info[label]== False:
            logging.info(f"{label}: \033[31mFalse\033[0m")
        elif info[label] == "True" or info[label] == True:
            logging.info(f"{label}: \033[32mTrue\033[0m")
        else:
            logging.info(f"{label}: {info[label]}")

def clear_terminal():
    # Check if the operating system is Windows ('nt') or Unix-like ('posix')
    if os.name == 'nt':
        _ = os.system('cls')  # Command for Windows
    else:
        _ = os.system('clear') # Command for Linux/macOS

if args.setup == 'true':
    interface_info = {'Network Interface': 'Not set',
                    'Linked to Device': False,
                    'Lidar IP Address': '192.168.20.20',}

    client_info = {'Start Lidar': False,
                'Start Streaming to Foxglove': False,
                'Start Recording to Binary': False,
                'Launch Voyant Client API Interface': False}
    def home():
        clear_terminal()
        # Print home menu options
        options = [
            "Configure Network Interface",
            "Build Docker Container",
            "Configure Voyant Client",
            "Run Voyant Client",
            "Exit"
        ]
        choice = render_menu(options, prompt="Please select an option: ", title="Voyant Client Setup Home Menu", refresh=False)
        if choice == "Configure Network Interface":
            configure_network_interface()
        elif choice == "Build Docker Container":
            build_docker_container()
        elif choice == "Configure Voyant Client":
            configure_voyant_client()
        elif choice == "Run Voyant Client":
            run_voyant_client()
        elif choice == "Exit":
            logging.info("Exiting Voyant Client Setup.")
            exit(0)

    # Function to configure the network interface
    def configure_network_interface():
        clear_terminal()
        options = [
            "Set Network Interface",
            "Linkup with Network Interface",
            "Check Network Interface Connection",
            "Set lidar IP Address",
            "Back"
        ]
        # Configure network interface
        render_info(interface_info, title="Current Network Interface Info")
        choice = render_menu(options, prompt="Please select an option: ", title="Network Interface Configuration Menu")
        if choice == "Set Network Interface":
            network_interface = get_network_interface()
            interface_info['Network Interface'] = network_interface
            logging.info(f"Network interface set to: {network_interface}")
            configure_network_interface()
        elif choice == "Linkup with Network Interface":
            linked_up = linkup_network_interface(interface_info['Network Interface'])
            interface_info["Linked to Device"] = linked_up
            configure_network_interface()
        elif choice == "Check Network Interface Connection":
            linked_up = check_network_interface_connection()
            interface_info["Linked to Device"] = linked_up
            configure_network_interface()
        elif choice == "Set lidar IP Address":
            logging.info(f"Current IP address: {interface_info['Lidar IP Address']}")
            ip_address = input("Please enter new lidar IP address (default is 192.168.20.20): ")
            logging.info(f"Lidar IP address set to: {ip_address}")
            interface_info['Lidar IP Address'] = ip_address
            configure_network_interface()
        elif choice == "Back":
            home()

    # Function to get the network interface associated with the lidar
    def get_network_interface():
        clear_terminal()
        # Collect all network interfaces
        network_interfaces = run_command('ip addr', capture=True).split('\n')
        # Parse the output to isolate interface names
        interface_names = []
        ethernet_extensions = ["eth", "eno", "enx"]
        for network_interface in network_interfaces:
            if len(network_interface) > 0 and network_interface[0].isnumeric():
                interface_name = network_interface.replace(" ", "").split(":")[1]
                if any(ext in interface_name for ext in ethernet_extensions):
                    interface_name = [interface_name, "\033[32m<- likely lidar\033[0m"]
                interface_names.append(interface_name)
        interface_name = render_menu(interface_names, prompt="If network interface is not present, check ethernet connection and refresh.\nPlease select network interface associated with lidar.", title="Available Network Interfaces", refresh=True, cancel=True)
        if interface_name == "Refresh":
            logging.info("Refreshing network interfaces...")
            return get_network_interface()
        elif interface_name == "Cancel":
            logging.info("Cancelling network interface selection.")
            configure_network_interface()
        else:
            logging.info(f"Selected network interface: {interface_name}")
            return interface_name

    # Function to link up with the network interface
    def linkup_network_interface(selected_interface):
        clear_terminal()
        #  Link up with the selected interface. Skip process if the interface is already liked with
        if ip_exists_on_interface(selected_interface, "192.168.20.100/24"):
            logging.info("Address already assigned to lidar interface.")
        else:
            logging.info("Assigning IP address to lidar interface.")
            run_command(f"ip addr add 192.168.20.100/24 dev {selected_interface}")
        run_command(f"ip link set {selected_interface} up")

        # Verify connection
        logging.info(f"Network lidar interface {selected_interface} configured with IP address. Testing connection.")
        if not is_device_reachable("192.168.20.20"):
            logging.error("Lidar device is unresponsive. \033[31mPlease check the connection and ensure the device is powered on, then attempt to reconnect.\033[0m")
            return False
        else:
            logging.info("Connection to lidar device created and verified.")
            return True

    # Function to check if the network interface is connected to the device
    def check_network_interface_connection():
        clear_terminal()
        # Check if the network interface is connected to the device
        if not is_device_reachable("192.168.20.20"):
            logging.error("\033[31mLidar device is unresponsive.\033[0m Please check the connection and ensure the device is powered on, then attempt to reconnect.")
            return False
        else:
            logging.info("Connection to lidar device verified.")
            return True

    # Function to build the Docker container
    def build_docker_container():
        clear_terminal()
        options = ["Yes, Build the Docker Container", "No, Take Me Back"]
        choice= render_menu(options, prompt="Would you like to build the Docker container?: ", title="Docker Container Build Menu", note="Building the Docker container is only required if you have never built it since last boot-up or if changes have been made since the last build. The build prossess can take a while, so I would recommend having a good book nearbye.\nWARNING: Might disconnect lidar. If you have already configured the network interface, you will need to reconfigure it after building the Docker container.")
        if choice == "Yes, Build the Docker Container":
            run_command("docker build --no-cache -t voyant-sdk-container -f docker/Dockerfile .")
            home()
        elif choice == "No, Take Me Back":
            home()

    # Function to configure the Voyant Client
    def configure_voyant_client():
        clear_terminal()
        options = ["Start Lidar",
                "Start Streaming to Foxglove",
                "Start Recording to Binary",
                "Launch Voyant Client API Interface",
                "Set all False",
                "Back"]
        render_info(client_info, title="Current Voyant Client Configuration")
        choice = render_menu(options, prompt="Please select an option to flip its value: ", title="Voyant Client Configuration Menu", note = "If set to True, the listed action will occur upon starting the Voyant Client automiticaly. If set to false, the action will not occur until you manually command it to inside the Voyant Client.")
        if choice == "Start Lidar":
            if client_info['Start Lidar']:
                client_info['Start Lidar'] = False
                client_info['Start Streaming to Foxglove'] = False
                client_info['Start Recording to Binary'] = False
            else:
                client_info['Start Lidar'] = True
            configure_voyant_client()
        elif choice == "Start Streaming to Foxglove":
            if client_info['Start Streaming to Foxglove']:
                client_info['Start Streaming to Foxglove'] = False
                client_info['Start Recording to Binary'] = False
            else:
                client_info['Start Streaming to Foxglove'] = True
                client_info['Start Lidar'] = True
                client_info['Launch Voyant Client API Interface'] = False
            configure_voyant_client()
        elif choice == "Start Recording to Binary":
            if client_info['Start Recording to Binary']:
                client_info['Start Recording to Binary'] = False
            else:
                client_info['Start Recording to Binary'] = True
                client_info['Start Streaming to Foxglove'] = True
                client_info['Start Lidar'] = True
                client_info['Launch Voyant Client API Interface'] = False
            configure_voyant_client()
        elif choice == "Launch Voyant Client API Interface":
            if client_info['Launch Voyant Client API Interface']:
                client_info['Launch Voyant Client API Interface'] = False
            else:
                client_info['Launch Voyant Client API Interface'] = True
                client_info['Start Lidar'] = False
                client_info['Start Streaming to Foxglove'] = False
                client_info['Start Recording to Binary'] = False
            configure_voyant_client()
        elif choice == "Set all False":
            client_info['Start Lidar'] = False
            client_info['Start Streaming to Foxglove'] = False
            client_info['Start Recording to Binary'] = False
            client_info['Launch Voyant Client API Interface'] = False
            configure_voyant_client()
        elif choice == "Back":
            home()

    # Function to run the Voyant Client in a Docker container
    def run_voyant_client():
        clear_terminal
        # if interface_info['Network Interface'] != 'Not set':
        #     if not is_device_reachable("192.168.20.20"):
        #         logging.error("\033[31mLidar device is unresponsive.\033[0m Please check the connection and ensure the device is powered on, then attempt to reconnect.")
        #         return False
        #     else:
        #         logging.info("Connection to lidar device verified.")
        #         return True
        render_info(interface_info, title="Current Network Interface Info")
        render_info(client_info, title="Current Voyant Client Configuration")
        options = ["Start Voyant Client", "Back"]
        choice = render_menu(options, prompt="Please select an option: ", title="Voyant Client Run Menu", note="If you have not configured the network interface or the Voyant Client or built the Docker Container (if necessary), please do so before running the client.")
        data = ""
        for info in client_info.keys():
            if client_info[info]:
                data += "t"
            elif not client_info[info]:
                data += "f"
        data += interface_info['Lidar IP Address']
        if choice == "Start Voyant Client":
            try:
            #     subprocess.run([
            #     "gnome-terminal",
            #     "--",
            #     "bash", "-c",
            #     "docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash; exec bash"
            # ])
                subprocess.run([
                    "gnome-terminal",
                    "--",
                    "bash", "-c",
                    f"docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container bash -c 'python3 /workspace/automated_voyant_client_setup.py --setup false --data {data}; exec bash'"
                    ])
            except Exception as e:
                run_command("docker stop voyant-sdk-container")
                run_command("docker rm voyant-sdk-container")
                # subprocess.run([
                #     "gnome-terminal",
                #     "--",
                #     "bash", "-c",
                #     "docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container /bin/bash; exec bash"
                # ])
                subprocess.run([
                    "gnome-terminal",
                    "--",
                    "bash", "-c",
                    f"docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container bash -c 'python3 /workspace/automated_voyant_client_setup.py --setup false --data {data}; exec bash'"
                    ])
            logging.info("Voyant Client setup completed successfully. You can now use the Voyant SDK inside the Docker container. For more information, refer to the documentation at https://voyant-photonics.github.io/. Thank you for using the Voyant Client Setup Script, exiting.")
            exit(0)
            # home()
        elif choice == "Back":
            home()

    home()  # Start the setup process
else:
    def cleanup():
        logging.warning("Stopping lidar")
        run_command("voyant_lidar_client --endpoint stop")

    def signal_handler(sig, frame):
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)   # Handles Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Handles kill

    lidar_info = {'Running': False,
                  'Lidar IP Address': '192.168.20.20'}

    client_info = {'Start Lidar': False,
                'Start Streaming to Foxglove': False,
                'Start Recording to Binary': False,
                'Launch Voyant Client API Interface': False}
    # Voyant Client in API Interface Mode
    logging.info("Running Voyant Client API Interface Mode.")
    if not args.data:
        logging.error("No data provided to the Voyant Client API Interface. Running under default parameters.")
    else:
        for i, key in enumerate(client_info.keys()):
            if args.data[i] == "t":
                client_info[key] = True
            elif args.data[i] == "f":
                client_info[key] = False
        lidar_info['Lidar IP Address'] = "".join(args.data[3:])

    try:
        def home():
            # Print home menu options
            options = [
                "Start/Stop Voyant lidar",
                "Start Streaming to Foxglove",
                "Start Recording to Binary",
                "Configure Lidar",
                "Miscellaneous Options",
                "Exit"
            ]
            choice = render_menu(options, prompt="Please select an option: ", title="Voyant Client Home Menu", refresh=False)
            if choice == "Start/Stop Voyant lidar":
                start_stop_lidar()
            elif choice == "Start Streaming to Foxglove":
                start_streaming()
            elif choice == "Start Recording to Binary":
                configure_voyant_client()
            elif choice == "Configure Lidar":
                run_voyant_client()
            elif choice == "Miscellaneous Options":
                misc_config()
            elif choice == "Exit":
                logging.info("Exiting Voyant Client.")
                exit(0)

        # Function to start or stop the lidar
        def start_stop_lidar():
            if lidar_info['Running']:
                options = [
                    "Yes, Stop Lidar",
                    "No, take Me Back"
                ]
            elif not lidar_info['Running']:
                options = [
                    "Yes, Start Lidar",
                    "No, take Me Back"
                ]

            render_info(lidar_info, title="Current lidar Info")
            choice = render_menu(options, prompt="Please select an option: ", title="Lidar Start/Stop Menu")
            if choice == "Yes, Stop Lidar":
                run_command("voyant_lidar_client --endpoint stop")
                lidar_info['Running'] = False
                start_stop_lidar()
            elif choice == "Yes, Start Lidar":
                run_command("voyant_lidar_client --endpoint start")
                lidar_info['Running'] = True
                start_stop_lidar()
            elif choice == "No, take Me Back":
                home()

        # Function to start streaming the lidar data to Foxglove
        def start_streaming():
            options = [
                    "Yes, Start Streaming to Foxglove",
                    "No, take Me Back"
                    ]
            render_info(lidar_info, title="Current lidar Info")
            choice = render_menu(options, prompt="Please select an option: ", title="Foxglove Start Streaming Menu", note="This will start streaming the lidar data to Foxglove Studio and open a new terminal. To stop streaming, kill the process in the new terminal by pressing ctrl C in the new terminal and then closing it.")
            if choice == "Yes, Start Streaming to Foxglove":
                run_command("voyant_foxglove_bridge --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100")
                start_streaming()
            elif choice == "No, take Me Back":
                home()

        # Function to start recording the lidar data to a binary file
        def start_recording():
            options = [
                    "Yes, I Have Read the Instructions. Start Recording to Binary",
                    "Back",
                    ]
            render_info(lidar_info, title="Current lidar Info")
            choice = render_menu(options, prompt="Please select an option: ", title="Binary Recording Start Menu", note="This will start streaming the lidar data. To record it, you will need to open a new terminal and enter this container by running 'docker exec -it voyant-sdk-container bash', then start recording by running 'voyant_logger_binary --output my_first_recording.bin --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100")
            if choice == "Yes, I Have Read the Instructions. Start Recording to Binary":
                run_command("voyant_foxglove_bridge --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100")
                start_recording()
            elif choice == "Back":
                home()

        # Function to check if the network interface is connected to the device
        def configure_lidar():
            logging.info("Configuring Lidar...")

        # Function to build the Docker container
        def misc_config():
            logging.info("Miscellaneous Options Menu")

        if client_info['Start Lidar']:
            run_command("voyant_lidar_client --endpoint start")
            lidar_info['Running'] = True
        if client_info['Start Streaming to Foxglove']:
            if not client_info['Start Recording to Binary']:
                run_command("voyant_foxglove_bridge --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100")
        if client_info['Start Recording to Binary']:
            logging.info("Starting recording to binary. Please open a new terminal and enter the container by running 'docker exec -it voyant-sdk-container bash', then start recording (after steaming has started) by running 'voyant_logger_binary --output my_first_recording.bin --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100'.")
            choice = input("I have read the instructions. Start streaming to Foxglove? (y/n): ").strip().lower()
            if choice == 'y':
                        run_command("voyant_foxglove_bridge --bind-addr 0.0.0.0:4444 --group-addr 224.0.0.0 --interface-addr 192.168.20.100")
            else:
                logging.info("Not starting streaming to Foxglove.")
        if client_info['Launch Voyant Client API Interface']:
            home()
    except Exception as e:
        cleanup()
        raise
