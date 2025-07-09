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

import voyant_lidar_client_utilities as util

def run_command(command, capture=False): # Runs a shell command and returns the output if capture is True
    result = subprocess.run(command, env=env, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        raise Exception(f"Command '{command}' failed with error: {result.stderr}")
    if capture:
        return result.stdout
