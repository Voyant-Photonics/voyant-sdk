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

parser = argparse.ArgumentParser(description="Runs as wrapper of Voyant API")

parser.add_argument('--lidar-network-interface', required=True, help='The network interface of the lidar.')

args = parser.parse_args()

status = {
    'Lidar On': False,
    'Streaming To Foxglove': False,
    'Recording to Binary': False
}
info = {
    'Lidar IP Address': '192.168.20.20',
    'Lidar Network Interface': args.lidar_network_interface,
    'Streaming Subprosses': 'Not Created',
    'Recording Subprosses': 'Not Created'
}

def cleanup():
    logging.warning("Stopping lidar")
    if status['Recording to Binary']:
        util.stop_subprosses(info['Recording Subprosses'])
        info['Recording Subprosses'] = 'Not Created'
    if status['Streaming To Foxglove']:
        util.stop_subprosses(info['Streaming Subprosses'])
        info['Streaming Subprosses'] = 'Not Created'
    util.run_command("voyant_lidar_client --endpoint stop")

def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)   # Handles Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Handles kill

def update_status(full_check=False):
    if full_check:
        status['Lidar On'] = util.is_device_streaming(info['Lidar IP Address'], info['Lidar Network Interface'])
    if info['Streaming Subprosses'] != 'Not Created':
        status['Streaming To Foxglove'] = util.is_process_running(info['Streaming Subprosses'])
    if info['Recording Subprosses'] != 'Not Created':
        status['Recording to Binary'] = util.is_process_running(info['Recording Subprosses'])

def home():
    # update_status()
    options = [
        (['Stop Lidar', ('| \033[31mStreaming\033[0m - will stop streaming if selected.' if status['Streaming To Foxglove'] else ''), ('| \033[31mRecording\033[0m - will stop recording if selected.' if status['Recording to Binary'] else '')] if status['Lidar On'] else 'Start Lidar'),
        (['Stop Streaming to Foxglove', ('| \033[31mRecording\033[0m - will stop recording if selected.' if status['Recording to Binary'] else '')] if status['Streaming To Foxglove'] else ['Start Streaming to Foxglove', ('| \033[31mLidar Not On\033[0m - will turn on lidar if selected.' if status['Lidar On'] == False else 'Start Streaming to Foxglove')]),
        ('Stop Recording to Binary' if status['Recording to Binary'] else ['Start Recording to Binary', ('' if status['Streaming To Foxglove'] else '| \033[31mLidar Not On\033[0m - will turn on lidar if selected.'), ('' if status['Streaming To Foxglove'] else '| \033[31mNot Streaming\033[0m - will start streaming if selected.')]),
        'Update Status',
        'Configure Lidar',
        'Quit'
        ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    choice = util.render_menu(options=options, title="Voyant Lidar Client Home", note="Welcome to the Voyant Lidar Client!")
    if choice == ('Stop Lidar' if status['Lidar On'] else 'Start Lidar'):
        start_stop_lidar()
        home()
    elif choice == ('Stop Streaming to Foxglove' if status['Streaming To Foxglove'] else 'Start Streaming to Foxglove'):
        start_stop_streaming()
        home()
    elif choice == ('Stop Recording to Binary' if status['Recording to Binary'] else 'Start Recording to Binary'):
        start_stop_recording()
        home()
    elif choice == 'Update Status':
        update_status(full_check=True)
        home()
    elif choice == 'Configure Lidar':
        home()
    elif choice == 'Quit':
        logging.info("Quitting Voyant Client Setup.")
        exit(0)

def start_stop_lidar():
    update_status()
    if status['Lidar On']:
        if status['Recording to Binary']:
            util.stop_subprosses(info['Recording Subprosses'])
            info['Recording Subprosses'] = 'Not Created'
            status['Recording to Binary'] = False
        if status['Streaming To Foxglove']:
            util.stop_subprosses(info['Streaming Subprosses'])
            info['Streaming Subprosses'] = 'Not Created'
            status['Streaming To Foxglove'] = False
        util.run_command('voyant_lidar_client --endpoint stop')
        status['Lidar On'] = False
    else:
        util.run_command('voyant_lidar_client --endpoint start')
        status['Lidar On'] = True

def start_stop_streaming():
    update_status()
    if status['Streaming To Foxglove']:
        if status['Recording to Binary']:
            util.stop_subprosses(info['Recording Subprosses'])
            info['Recording Subprosses'] = 'Not Created'
            status['Recording to Binary'] = False
        util.stop_subprosses(info['Streaming Subprosses'])
        info['Streaming Subprosses'] = 'Not Created'
        status['Streaming To Foxglove'] = False

    else:
        if status['Lidar On'] == False:
            start_stop_lidar()
        info['Streaming Subprosses'] = util.run_command_as_subprosses([
        "voyant_foxglove_bridge",
        "--bind-addr", "0.0.0.0:4444",
        "--group-addr", "224.0.0.0",
        "--interface-addr", "192.168.20.100"
    ])
        status['Streaming To Foxglove'] = True

def start_stop_recording():
    update_status()
    if status['Recording to Binary']:
        util.stop_subprosses(info['Recording Subprosses'])
        info['Recording Subprosses'] = 'Not Created'
        status['Recording to Binary'] = False
    else:
        if status['Lidar On'] == False:
            start_stop_lidar()
        if status['Streaming To Foxglove'] == False:
            info['Streaming Subprosses'] = util.run_command_as_subprosses([
            "voyant_foxglove_bridge",
            "--bind-addr", "0.0.0.0:4444",
            "--group-addr", "224.0.0.0",
            "--interface-addr", "192.168.20.100"
        ])
            status['Streaming To Foxglove'] = True
        info['Streaming Subprosses'] = util.run_command_as_subprosses([
        "voyant_logger_binary",
        "--output", "my_first_recording.bin",
        "--bind-addr", "0.0.0.0:4444",
        "--group-addr", "224.0.0.0",
        "--interface-addr", "192.168.20.100"
    ])
        status['Recording to Binary'] = True

home()
