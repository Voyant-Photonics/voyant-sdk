# Standard library imports
import sys
import argparse
import logging
import os
import signal
import socket
import subprocess


# Related third-party imports

# Local application/library specific imports

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command:str|list, capture=False, timeout:int|float|None=None, live_output=False) -> str|None:
    """
    Runs the provided command in the active terminal.

    This function will run the provided command (either a string or a list) as a terminal command in the active terminal. It will aujust how it runs the command based on the nature of the command and how it is formatted.

    Parameters
    ----------
    command : string/list
        The command you wish to run. If a string, command will be run in a shell. If a list, command will be run outside of a shell. If a list, indexes of list should be a arguments.
    capture : boolean, optional
        Controls if output of command is captured and returned by function (True) or if output is printed in terminal(False). By default, this parameter is set to False.
    timeout : int/float, optional
        Controls how long (in seconds) the command is allowed to run before Python forcibly stops it. Defaults to None (no time limit).
    live_output : boolean, optional
        If True, will us Popen for more control and flexibility (e.g., for streaming output, handling input, or advanced process management). Overrides capture functionality if True.

    Returns
    -------
    String
        If capture is True and live_output is False, will return string of terminal output.

    Raises
    ------
    ExceptionType
        Will raise any exception, and will list associated command that caused it.

    Examples
    --------
    >>> run_command("echo 'Hello, World!'", capture=True)
    # Expected output
    'Hello, World!'
    """

    if isinstance(command, str) and not live_output:
        shell = True
    else:
        shell = False

    try:
        if live_output:
            # Show output in real time
            process = subprocess.Popen(command, shell=isinstance(command, str), env=os.environ.copy())
            process.communicate(timeout=timeout)
            if process.returncode != 0:
                logging.error(f"Command '{command}' failed with return code {process.returncode}")
                raise subprocess.CalledProcessError(process.returncode, command)
            return None
        else:
            result = subprocess.run(
                command,
                env=os.environ.copy(),
                shell=shell,
                capture_output=capture,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0:
                logging.error(f"Command '{command}' failed: {result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
            return result.stdout if capture else None
    except Exception as e:
        logging.error(f"Exception running command '{command}': {e}")
        raise

def render_menu(options:list, prompt="Please select an option", clear=False, title:str|None=None, note:str|list|None=None, warning:str|list|None=None) -> str:
    """
    Creates an interactive menu in terminal.

    This function renders a multiple choice style menu in the active terminal, and will then prompt the user for an input. Once a valid input is entered, this function will return the user's selection as a string. This function will consider both any number associated with an option and an option itself as a valid input, and will deal with invalid inputs.

    Parameters
    ----------
    options : list
        A list of options. A python list containing the options (unnumbered) as strings or as lists. If the option is a list, all indexes of the list will be combined into one string separated by spaces and displayed in a single line as that option. However, only the first index of the list will be returned if that option is selected. Can be useful if you want to add status to certain options. Will list the options in the order stored in this list.
    prompt : string, optional
        If set, will dictate the prompt at the end of the menu. If let unset, defaults to 'Please select an option". Colon and end-space will be added if not provided.
    clear : boolean, optional
        If set to True, the function will clear the terminal before rendering the menu. Defaults to False.
    title : string, optional
        If set, this string will be displayed as the title of the menu at the top of the rendering. If not set, not title will be rendered.
    note : string | list, optional
        If set, this string will be displayed below the title (if present) and before the list of options. If a list of strings, each string will be printed on it's own line. Useful for providing any needed context. Will be printed after 'Note: '.
    warning : string | list, optional
        Like note, but will be printed after 'WARNING: ', which will be in red. Useful for any urgent information you do not want your users to miss. If both note and warning are used, warning(s) will be printed after note(s).

    Returns
    -------
    String
        Will return a string of the option that the user selected as it was in the options list provided as the options variable when this function was called.

    Examples
    --------
    >>> render_menu(options=["Turn Off", ["Turn On", "| Will boot in safe mode:", "True"], "Restart"], clear=True, title="Power Control Menu", note="Menu for controlling power to device.", warning="System will need 45 seconds to power down after Power Off command is sent. Do not unplug from power until the indicator light goes out."):
    # Expected output in active terminal
    # 2025-07-09 12:57:41,593 - INFO - =====-Power Control Menu-=====
    # 2025-07-09 12:57:41,593 - INFO - Note: Menu for controlling power to device.
    # 2025-07-09 12:57:41,593 - WARNING - WARNING: System will need 45 seconds to power down after Power Off command is sent. Do not unplug from power until the indicator light goes out.
    # 2025-07-09 12:57:41,593 - INFO - ===-Available Options
    # 2025-07-09 12:57:41,593 - INFO -     1. Turn Off
    # 2025-07-09 12:57:41,593 - INFO -     2. Turn On | Will boot in safe mode: True
    # 2025-07-09 12:57:41,593 - INFO -     3. Restart
    # Please select an option:
    """
    invalid_selection=False
    while True:
        if clear:
            clear_terminal()
        if isinstance(title, str):
            logging.info(f"=====-{title.strip()}-=====")
        if isinstance(note, str):
            logging.info(f"Note: {note.strip()}")
        elif isinstance(note, list):
            for n in note:
                logging.info(f"Note: {n.strip()}")
        if isinstance(warning, str):
            logging.info(f"\033[31mWARNING:\033[0m {warning.strip()}")
        elif isinstance(warning, list):
            for w in warning:
                logging.info(f"\033[31mWARNING:\033[0m {w.strip()}")
        logging.info("===-Available Options")
        display_options = options.copy()
        for i, option in enumerate(display_options):
            if type(option) == list:
                option = " ".join(option)
                display_options[i] = display_options[i][0]
            logging.info(f"    {i + 1}. {option}")
        if invalid_selection:
            logging.info("\033[31mInvalid selection:\033[0m please try again.")
        prompt = prompt.strip()
        if prompt[-1] != ":":
            prompt += ":"
        choice = input(f"{prompt} ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return display_options[int(choice) - 1]
        elif choice.lower() in [option.lower() for option in display_options]:
            return display_options[[option.lower() for option in display_options].index(choice.lower())]
        else:
            invalid_selection = True

def render_info(info:dict, clear=False, title:str|None=None, note:str|list|None=None, warning:str|list|None=None, colorize=False):
    """
    Creates an info readout.

    This function provieds a way to print the status of variables in a standardized way.

    Parameters
    ----------
    info : dict
        A dictionary of data, where each key is the name or title of the data value as a string, and the associated value is a integer, float, string, or a list of any of them.
    clear : boolean
        If set to true, this function will clear the console before rendering the info.
    title : string, optional
        If set, this string will be displayed as the title of the info readout at the top of the rendering. If not set, not title will be rendered.
    note : string, optional
        If set, this string will be displayed below the title (if present) and before the info list. If a list of strings, each string will be printed on it's own line. Useful for providing any need context. Will be printed after 'Note: '.
    warning : string, optional
        Like note, but will be printed after 'WARNING: ', which will be in red. Useful for any urgent information you do not want your users to miss. If both note and warning are used, warning(s) will be printed after note(s).
    colorize : boolean:
        If set to true, the function will colorize certain elements of data. All True and False values, either as strings or as booleans, will be colored green or red respecitivly. Additionally, positive numbers will be green, and negative numbers will be red.

    Examples
    --------
    >>> render_info({"On": True, "Power Draw": power, "Connected": "Unsure"},clear = True, title="Info Dump", note="This is the system readout.", warning="Your system is about to explode. Run.", colorize=True):
    # Expected output in active terminal
    # 2025-07-09 14:48:32,405 - INFO - =====-Info Dump-=====
    # 2025-07-09 14:48:32,405 - INFO - Note: This is the system readout.
    # 2025-07-09 14:48:32,405 - INFO - WARNING: Your system is about to explode. Run.
    # 2025-07-09 14:48:32,405 - INFO - ===-Info
    # 2025-07-09 14:48:32,405 - INFO - On: True
    # 2025-07-09 14:48:32,405 - INFO - Power Draw: -20
    # 2025-07-09 14:48:32,405 - INFO - Connected: Unsure
    """
    if clear:
        clear_terminal()
    if isinstance(title, str):
        logging.info(f"=====-{title.strip()}-=====")
    if isinstance(note, str):
        logging.info(f"Note: {note.strip()}")
    elif isinstance(note, list):
        for n in note:
            logging.info(f"Note: {n.strip()}")
    if isinstance(warning, str):
        logging.info(f"\033[31mWARNING:\033[0m {warning.strip()}")
    elif isinstance(warning, list):
        for w in warning:
            logging.info(f"\033[31mWARNING:\033[0m {w.strip()}")
    if isinstance(title, str) or isinstance(note, str) or isinstance(note, list) or isinstance(warning, str) or isinstance(warning, list):
        logging.info("===-Info")
    for label in info.keys():
        if colorize:
            if info[label] == "False" or not info[label]:
                logging.info(f"{label}: \033[31mFalse\033[0m")
            elif info[label] == "True" or info[label] == True:
                logging.info(f"{label}: \033[32mTrue\033[0m")
            elif type(info[label]) == int or type(info[label]) == float:
                if info[label] >= 0:
                    logging.info(f"{label}: \033[32m{str(info[label])}\033[0m")
                elif info[label] < 0:
                    logging.info(f"{label}: \033[31m{str(info[label])}\033[0m")
            else:
                logging.info(f"{label}: {info[label]}")
        else:
            logging.info(f"{label}: {info[label]}")

def clear_terminal():
    """
    Clears active terminal
    """
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def is_device_reachable(ip, port=22, timeout=3):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError:
        return False

def is_device_reachable(ip:str, port:int=22, timeout:float=3) -> bool:
    """
    Checks if a device at the given IP and port is reachable via TCP.

    Parameters
    ----------
    ip : str
        The IP address of the device to check.
    port : int, optional
        The port to attempt to connect to. Defaults to 22.
    timeout : float, optional
        Timeout in seconds for the connection attempt. Defaults to 3.

    Returns
    -------
    bool
        True if the device is reachable, False otherwise.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except OSError as e:
        logging.debug(f"Device at {ip}:{port} not reachable: {e}")
        return False

def ip_exists_on_interface(interface:str, ip:str) -> bool:
    """
    Checks if a given ip address exits on the specified network interface.

    Parameters
    ----------
    interface : string
        The name of the network interface you wish to check on.
    ip : string
        The IP address to check to existence of (in most cases, the ip of this device)

    Returns
    -------
    boolean
        True if ip is present already on network interface, False otherwise.
    """
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

import subprocess

def docker_image_exists(image_name: str) -> bool:
    """
    Returns True if a Docker image with the given name (optionally with tag) exists locally.
    """
    try:
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        images = [line.strip() for line in result.stdout.splitlines()]
        if ":" not in image_name:
            return any(img.startswith(f"{image_name}:") for img in images)
        else:
            return image_name in images
    except subprocess.CalledProcessError:
        return False
