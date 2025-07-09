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

def run_command(command: str | list, capture=False, timeout: int | None = None, live_output=False):
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

def render_menu(options, prompt="Please input response: ", clear=False, title:str|None=None, note:str|None=None, warning:str|None=None):
    """
    Creates a interactive menu in terminal.

    This function renders a multiple choice style menu in the active terminal, and will then prompt the user for an input. Once a valid input is entered, this function will return the user's selection as a string. This function will consider both any number associated with an option and an option itself as a valid input, and will deal with invalid inputs.

    """
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
