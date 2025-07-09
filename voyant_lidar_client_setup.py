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

# Declare status and info dictionaries:
status = {
    'Docker Container Built': False,
    'Linked Up': False
}
info = {
    'Docker Container Name': 'voyant-sdk-container',
    'Network Interface': 'Not Set',
    'Lidar IP Address': '192.168.20.20'
}

def update_status():
    status["Docker Container Built"] = util.docker_image_exists(image_name = info['Docker Container Name'])
    if info['Network Interface'] != 'Not Set' and status["Linked Up"] == True:
        status['Linked Up'] = util.is_device_reachable(ip=status["Lidar IP Address"],timeout=3)

def home():
    update_status()
    options = [
        'Build Docker Container',
        'Select Lidar Network Interface & Link Up',
        ['Set Lidar IP Address','(required if IP address of lidar has been changed from default)'],
        ['Run Voyant Lidar Client', ('| \033[31mRequired\033[0m - Build Docker Container' if status['Docker Container Built'] == False else ''), ('| \033[31mRequired\033[0m - Select Lidar Network Interface & Link Up' if status['Linked Up'] == False else '')],
        'Quit'
    ]
    util.render_info(info=info, clear=True, title='Setup Information and Status')
    util.render_info(info=status,colorize=True)
    choice = util.render_menu(options=options, title="Voyant Lidar Client Setup Home")
    if choice == 'Build Docker Container':
        build_docker_container()
    elif choice == 'Select Lidar Network Interface & Link Up':
        print("Okay")
    elif choice == 'Set Lidar IP Address':
        print("Okay")
    elif choice == 'Run Voyant Lidar Client':
        print("Okay")
    elif choice == 'Quit':
        logging.info("Exiting Voyant Client Setup.")
        exit(0)

def build_docker_container():
    update_status()
    options = [
        'Build Docker Container',
        'Back'
    ]
    util.render_info(info={k: info[k] for k in ['Docker Container Name']}, clear=True, title='Docker Information and Status')
    util.render_info(info={k: status[k] for k in ['Docker Container Built']},colorize=True)
    choice = util.render_menu(options=options, title="Build Docker Container Menu", note='Only needed if Docker Container is not built or if it has been updated since last build')
    if choice == 'Build Docker Container':
        util.run_command("docker build --no-cache -t voyant-sdk-container -f docker/Dockerfile .")
        home()
    elif choice == 'Back':
        home()

home()
