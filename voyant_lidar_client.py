import sys
import argparse
import logging
import signal
import voyant_lidar_client_utilities as util
from datetime import datetime

parser = argparse.ArgumentParser(description="Runs as wrapper of Voyant API")
parser.add_argument('--lidar-network-interface', required=True, help='The network interface of the lidar.')
parser.add_argument('--container-name', required=True, help='Name of the Docker Container made by the setup script.')
parser.add_argument('--lidar-ip-addr', required=True, help='The IP address of the lidar')
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

status = {
    'Lidar On': False,
    'Streaming To Foxglove': False,
    'Recording to Binary': False,
    'Playing Recording': False
}
info = {
    'Lidar IP Address': args.lidar_ip_addr,
    'Lidar Network Interface': args.lidar_network_interface,
    'Container Name': args.container_name,
    'Streaming Subprosses': 'Not Created',
    'Recording Subprosses': 'Not Created',
    'Playback Subprosses': 'Not Created'
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
    if info['Playback Subprosses'] != 'Not Created':
        status['Playing Recording'] = util.is_process_running(info['Recording Subprosses'])


def home():
    update_status()
    options = [
        (['Stop Lidar', ('| \033[31mStreaming\033[0m - will stop streaming if selected.' if status['Streaming To Foxglove'] else ''), ('| \033[31mRecording\033[0m - will stop recording if selected.' if status['Recording to Binary'] else '')] if status['Lidar On'] else 'Start Lidar'),
        (['Stop Streaming to Foxglove', ('| \033[31mRecording\033[0m - will stop recording if selected.' if status['Recording to Binary'] else '')] if status['Streaming To Foxglove'] else ['Start Streaming to Foxglove', ('| \033[31mLidar Off\033[0m - will turn on lidar if selected.' if status['Lidar On'] == False else 'Start Streaming to Foxglove'), ('| \033[31mPlaying Recording.\033[0m Will stop playback if selected.' if status['Playing Recording'] else '')]),
        ('Stop Recording to Binary' if status['Recording to Binary'] else ['Start Recording to Binary', ('' if status['Streaming To Foxglove'] else '| \033[31mLidar Off\033[0m - will turn on lidar if selected.'), ('' if status['Streaming To Foxglove'] else '| \033[31mNot Streaming\033[0m - will start streaming if selected.'), ('| \033[31mPlaying Recording.\033[0m Will stop playback if selected.' if status['Playing Recording'] else '')]),
        ('Stop Recording Playback' if status['Playing Recording'] else ['Select Recording to Playback', ('| \033[31mStreaming .\033[0m Will stop streaming if selected.' if status['Streaming To Foxglove'] else ''), ('| \033[31mRecording.\033[0m Will stop recording if selected.' if status['Recording to Binary'] else '')]),
        'Steaming Options',
        'Power Options',
        'Recording Options',
        'Playback Options',
        'Data Conversion and Utility Tools',
        'Update Status',
        'Quit'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    choice = util.render_menu(options=options, title="Voyant Lidar Client Home", note="Welcome to the Voyant Lidar Client! The options below are quickactions")
    if choice == ('Stop Lidar' if status['Lidar On'] else 'Start Lidar'):
        start_stop_lidar()
        home()
    elif choice == ('Stop Streaming to Foxglove' if status['Streaming To Foxglove'] else 'Start Streaming to Foxglove'):
        start_stop_streaming()
        home()
    elif choice == ('Stop Recording to Binary' if status['Recording to Binary'] else 'Start Recording to Binary'):
        start_stop_recording()
        home()
    elif choice == 'Playback Recordings':
        start_stop_playback()
        home()
    elif choice == 'Update Status':
        update_status(full_check=True)
        home()
    elif choice == 'Quit':
        logging.info("Quitting Voyant Client Setup.")
        cleanup()
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
            start_stop_recording()
        util.stop_subprosses(info['Streaming Subprosses'])
        info['Streaming Subprosses'] = 'Not Created'
        status['Streaming To Foxglove'] = False

    else:
        if status['Lidar On'] == False:
            start_stop_lidar()
        if status['Playing Recording']:
            start_stop_playback()
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
        if status['Playing Recording']:
            start_stop_playback()
        if status['Streaming To Foxglove'] == False:
            start_stop_streaming()
        file_name = f'lidar_recording_{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        info['Streaming Subprosses'] = util.run_command_as_subprosses([
        "voyant_logger_binary",
        "--output", f"{file_name.strip()}.bin",
        "--bind-addr", "0.0.0.0:4444",
        "--group-addr", "224.0.0.0",
        "--interface-addr", "192.168.20.100"
    ])
        status['Recording to Binary'] = True

def start_stop_playback():
    update_status()
    if status['Playing Recording']:
        util.stop_subprosses(info['Playback Subprosses'])
        status['Playing Recording'] = False
    else:
        if status['Recording to Binary']:
            start_stop_recording()
            status['Recording to Binary'] = False
        if status['Streaming To Foxglove']:
            start_stop_streaming()
            status['Streaming To Foxglove'] = False
        options = util.get_files_from_directory(directory_path='/workspace/recordings', file_extension='.bin')
        options.append('Back')
        choice = util.render_menu(options=options, prompt='Please select a recording to playback', clear=True, title='Lidar Recording Playback Menu', note='Once selected, the recording will begin to playback to foxglove in a loop')
        if choice == 'Back':
            home()
        else:
            info['Streaming Subprosses'] = util.run_command_as_subprosses([
            "voyant_playback_foxglove",
            "--input", choice,
            "--loopback"
        ])
            status['Playing Recording'] = True
    home()

try:
    home()
except Exception as e:
    cleanup()
    raise
