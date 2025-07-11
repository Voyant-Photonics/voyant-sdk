import logging
import subprocess
import voyant_lidar_client_utilities as util

status = {
    'Docker Container Built': False,
    'Linked Up': False
}
info = {
    'Docker Container Name': 'voyant-sdk-container',
    'Network Interface': 'Not Set',
    'Lidar IP Address': '192.168.20.20'
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_status():
    status["Docker Container Built"] = util.docker_image_exists(image_name = info['Docker Container Name'])
    if info['Network Interface'] != 'Not Set':
        status['Linked Up'] = util.is_device_reachable(ip=info["Lidar IP Address"])

def home():
    update_status()
    if info['Network Interface'] == 'Not Set' or status['Linked Up'] == True:
        options = [
            'Build Docker Container',
            'Select Lidar Network Interface & Link Up',
            ['Run Voyant Lidar Client', ('| \033[31mRequired\033[0m - Build Docker Container' if status['Docker Container Built'] == False else ''), ('| \033[31mRequired\033[0m - Select Lidar Network Interface & Link Up' if status['Linked Up'] == False else '')],
            'Misc Config Settings',
            'Refresh Info'
            'Quit'
            ]
    else:
        options = [
            'Build Docker Container',
            'Select Lidar Network Interface & Link-Up',
            'Retry Link-Up',
            ['Run Voyant Lidar Client', ('| \033[31mRequired\033[0m - Build Docker Container' if status['Docker Container Built'] == False else ''), ('| \033[31mRequired\033[0m - Select Lidar Network Interface & Link Up' if status['Linked Up'] == False else '')],
            'Misc Config Settings',
            'Refresh Info'
            'Quit'
            ]
    util.render_info(info=info, clear=True, title='Setup Information and Status')
    util.render_info(info=status,colorize=True)
    choice = util.render_menu(options=options, title="Voyant Lidar Client Setup Home")
    if choice == 'Build Docker Container':
        build_docker_container()
    elif choice == 'Select Lidar Network Interface & Link Up':
        select_lidar_interface_and_link()
    elif choice == 'Retry Link-Up':
        link_up()
        home()
    elif choice == 'Run Voyant Lidar Client':
        run_voyant_client()
    elif choice == 'Misc Config Settings':
        print("Open Config")
    elif choice == 'Refresh Info':
        home()
    elif choice == 'Quit':
        logging.info("Quitting Voyant Client Setup.")
        exit(0)

def build_docker_container():
    update_status()
    options = [
        ['Build Docker Container', ('| \033[32mDocker Container Build Already Present.\033[0m Only required if updates have been made to api, sdk, or Dockerfile since last build.' if status['Docker Container Built'] else '')],
        'Back'
    ]
    util.render_info(info={k: info[k] for k in ['Docker Container Name']}, clear=True, title='Docker Information and Status')
    util.render_info(info={k: status[k] for k in ['Docker Container Built']},colorize=True)
    choice = util.render_menu(options=options, title="Build Docker Container Menu")
    if choice == 'Build Docker Container':
        util.run_command("docker build --no-cache -t voyant-sdk-container -f docker/Dockerfile .")
        home()
    elif choice == 'Back':
        home()

def select_lidar_interface_and_link():
    interface = get_network_interface()
    if interface != 'Back':
        info['Network Interface'] = interface
        link_up()
    home()

def get_network_interface():
    while True:
        update_status()
        network_interfaces = util.run_command('ip addr', capture=True).split('\n')
        options = []
        ethernet_headers = ["eth", "eno", "enx"]
        for network_interface in network_interfaces:
            if len(network_interface) > 0 and network_interface[0].isnumeric():
                interface_name = network_interface.replace(" ", "").split(":")[1]
                if any(ethernet_header in interface_name for ethernet_header in ethernet_headers):
                    interface_name = [interface_name, "| Ethernet type connection. \033[32mLikely Lidar.\033[0m"]
                options.append(interface_name)
        options.append('Refresh')
        options.append('Back')
        util.render_info(info={k: info[k] for k in ['Network Interface']}, clear=True, title='Network Interface Information and Status')
        util.render_info(info={k: status[k] for k in ['Linked Up']},colorize=True)
        interface_name = util.render_menu(options, title="Available Network Interfaces", note='The lidar will be represented by an ethernet name (eth, en, etc.). The program will attempt to identify these for you. If there is more than one ethernet connection, or non at all, try disconnecting the lidar from this device, refreshing this menu, reconnecting the lidar, and refreshing again. The new connection is your lidar.')
        if interface_name == "Refresh":
            continue
        else:
            return interface_name.strip()

def link_up():
    if not util.ip_exists_on_interface(info['Network Interface'], "192.168.20.100/24"):
        util.run_command(f"ip addr add 192.168.20.100/24 dev {info['Network Interface']}")
    util.run_command(f"ip link set {info['Network Interface']} up")

def run_voyant_client():
    update_status()
    options=[
        ['Start Voyant Client', ('| \033[31mDocker Container Not Built.\033[0m Build the Docker Container before continuing.' if status['Docker Container Built'] == False else ''), ('| \033[31mLidar Not Linked Up.\033[0m Link up lidar to valid network interface before continuing.' if status['Linked Up'] == False else '')],
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Setup Information and Status')
    util.render_info(info=status,colorize=True)
    options = ["Start Voyant Client", "Back"]
    choice = util.render_menu(options, title="Voyant Client Run Menu", note="Running the Voyant Client will open a new terminal window inside of the Docker Container in which the Voyant Client will be running.", warning='Your lidar will not function properly if all of the required steps were not completed before running the Voyant Client. If there are any warnings next to the option to run the Voyant Client, please resolve them before continuing.')
    if choice == "Start Voyant Client":
        try:
            util.run_command("docker stop voyant-sdk-container")
            util.run_command("docker rm voyant-sdk-container")
            subprocess.run([
            "gnome-terminal",
            "--",
            "bash", "-c",
            f"docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container bash -c 'python3 /workspace/voyant_lidar_client.py --lidar-network-interface {info['Network Interface']}; exec bash'"
            ])
        except:
            subprocess.run([
            "gnome-terminal",
            "--",
            "bash", "-c",
            f"docker run --rm -it --name voyant-sdk-container --network host -v $(pwd):/workspace voyant-sdk-container bash -c 'python3 /workspace/voyant_lidar_client.py --lidar-network-interface {info['Network Interface']}; exec bash'"
            ])
        logging.info("Voyant Client setup completed successfully. You can now use the Voyant SDK inside the Docker container. For more information, refer to the documentation at https://voyant-photonics.github.io/. Thank you for using the Voyant Client Setup Script, exiting.")
        # exit(0)
    elif choice == "Back":
        home()

home()  # Start the setup process
