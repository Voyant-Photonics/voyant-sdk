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
        'Extended Tools',
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

def extended_options():
    options = [
        'Steaming Options',
        'Power Options',
        'Recording Options',
        'Playback Options',
        'Data Conversion and Utility Tools',]

def streaming_options():
    streaming_info = {
        'Point Filtering': False,
        'Mock Sim': False,
        'WebSocket Port': '8765',
        'Check Interval': '10',
        'Subprocess': 'Not Created'
    }
    update_status()
    options = [
        'Start Streaming with Point Filtering',
        'Start Streaming without Point Filtering',
        'Start a Mock Stream',
        'Do Not Start a Mock Stream',
        'Set Custom WebSocket Port',
        ['Set Pointcloud Check Interval', '| How often the api checks for another pointcloud(frame) from the lidar. This does not change the refresh rate of the lidar itself. Setting to anything over 10(default) will have no effect over than increasing performance draw.'],
        'Start Stream',
        'Stop Stream',
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    util.render_info(info=streaming_info)
    choice = util.render_menu(options=options, title="Streaming Options Menu", warning="No action protection in this menu. If command contradicts with current lidar state or will cause a crash, program will execute anyway.")
    if choice == 'Start Streaming with Point Filtering':
        streaming_info['Point Filtering'] = True
    elif choice == 'Start Streaming without Point Filtering':
        streaming_info['Point Filtering'] = False
    elif choice == 'Start a Mock Stream':
        streaming_info['Mock Sim'] = True
    elif choice == 'Do Not Start a Mock Stream':
        streaming_info['Mock Sim'] = False
    elif choice == 'Set Custom WebSocket Port':
        streaming_info['WebSocket Port'] = input('New WebSocket Port: ')
    elif choice == 'Set Pointcloud Check Interval':
        streaming_info['Check Interval'] = input('New Check Interval: ')
    elif choice == 'Start Stream':
        command = [
            'voyant_foxglove_bridge',
            '--ws-port', streaming_info['WebSocket Port'],
            '--bind-addr', '0.0.0.0:4444',
            '--group-addr', '224.0.0.0',
            '--interface-addr', ('127.0.0.1' if streaming_info['Mock Sim'] else '192.168.20.100'),
            '--check-interval', streaming_info['Check Interval'],

        ]
        if streaming_info['Point Filtering'] == False:
            command.append('--keep-invalid-points')
        streaming_info['Subprocess']=util.run_command_as_subprosses(command=command)
    elif choice == 'Stop Stream':
        util.stop_subprosses(streaming_info['Subprocess'])
        streaming_info['Subprocess'] = 'Not Created'
    if choice == 'Back':
        extended_options()
    else:
        streaming_options()

def power_options():
    update_status()
    options = [
        'Turn On Lidar',
        'Turn On Lidar - Force Restart',
        'Turn Off Lidar',
        ['Suspend Lidar', '| Will temporarily disable the on-device processing and streaming of LiDAR points; skips lengthy disable steps.'],
        ['Unsuspend Lidar', '| Will re-enable the on-device processing and streaming of LiDAR points; skips lengthy enable steps'],
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    choice = util.render_menu(options=options, title="Power Options Menu", warning="No action protection in this menu. If command contradicts with current lidar state or will cause a crash, program will execute anyway.")
    if choice == 'Turn On Lidar':
        util.run_command('voyant_lidar_client --endpoint start')
        status['Lidar On'] = True
    elif choice == 'Turn On Lidar - Force Restart':
        util.run_command('voyant_lidar_client --endpoint start --force-restart')
        status['Lidar On'] = True
    elif choice == 'Turn Off Lidar':
        util.run_command('voyant_lidar_client --endpoint stop')
        status['Lidar On'] = False
    elif choice == 'Suspend Lidar':
        util.run_command('voyant_lidar_client --endpoint stop --skip-disable')
        status['Lidar On'] = False
    elif choice == 'Unsuspend Lidar':
        util.run_command('voyant_lidar_client --endpoint start --skip-enable')
        status['Lidar On'] = False
    if choice == 'Back':
        extended_options()
    else:
        power_options()

def recording_options():
    recording_info = {
        'Point Filtering': False,
        'Output Path': 'my_recording.bin',
        'Time Limit': '0',
        'Frame Limit': '10',
        'Subprocess': 'Not Created'
    }
    update_status()
    options = [
        'Start Recording with Point Filtering',
        'Start Recording without Point Filtering',
        ['Set Frame Limit', '| Set to 0 for no frame limit'],
        ['Set Time Limit', '(seconds)', '| Set to 0 for no time limit'],
        'Set Output Path',
        'Start Recording',
        'Stop Recording',
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    util.render_info(info=recording_info)
    choice = util.render_menu(options=options, title="Recording Options Menu", warning="No action protection in this menu. If command contradicts with current lidar state or will cause a crash, program will execute anyway.")
    if choice == 'Start Recording with Point Filtering':
        recording_info['Point Filtering'] = True
    elif choice == 'Start Recording without Point Filtering':
        recording_info['Point Filtering'] = False
    elif choice == 'Set Frame Limit':
        recording_info['Frame Limit'] = input('Enter new frame limit: ')
    elif choice == 'Set Time Limit':
        recording_info['Time Limit'] = input('Enter new time limit(seconds): ')
    elif choice == 'Set Output Path':
        recording_info['Output Path'] = input('New output path: ')
    elif choice == 'Start Recording':
        command = [
            'voyant_logger_binary',
            '--output my_recording.bin', recording_info['Output Path'],
            '--bind-addr', '0.0.0.0:4444',
            '--group-addr', '224.0.0.0',
            '--interface-addr', '192.168.20.100',
            '--duration', recording_info['Time Limit'],
            '--frames', recording_info['Frame Limit']
        ]
        if recording_info['Point Filtering'] == False:
            command.append('--keep-invalid-points')
        recording_info['Subprocess']=util.run_command_as_subprosses(command=command)
    elif choice == 'Stop Recording':
        util.stop_subprosses(recording_info['Subprocess'])
        recording_info['Subprocess'] = 'Not Created'
    if choice == 'Back':
        extended_options()
    else:
        recording_options()

def playback():
    playback_info = {
        'Playback File': 'my_recording.bin',
        'Playback Rate': '1',
        'Loopback': True,
        'WebSocket Port': '8765',
        'Subprocess': 'Not Created',
        'Filter Points': False
    }
    update_status()
    options = [
        'Start Playback with Point Filtering',
        'Start Playback without Point Filtering',
        'Set Playback Rate',
        'Loopback',
        'Do Not Loopback',
        'Set WebSocket',
        'Set Playback File',
        'Start Playback',
        'Stop Playback',
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    util.render_info(info=playback_info)
    choice = util.render_menu(options=options, title="Playback Options Menu", warning="No action protection in this menu. If command contradicts with current lidar state or will cause a crash, program will execute anyway.")
    if choice == 'Start Playback with Point Filtering':
        playback_info['Filter Points'] = True
    elif choice == 'Start Playback without Point Filtering':
        playback_info['Filter Points'] = False
    elif choice == 'Set Playback Rate':
        playback_info['Playback Rate'] = input('Enter new playback rate: ')
    elif choice == 'Loopback':
        playback_info['Loopback'] = True
    elif choice == 'Do Not Loopback':
        playback_info['Loopback'] = False
    elif choice == 'Start Recording':
        command = [
            'voyant_logger_binary',
            '--output my_recording.bin', recording_info['Output Path'],
            '--bind-addr', '0.0.0.0:4444',
            '--group-addr', '224.0.0.0',
            '--interface-addr', '192.168.20.100',
            '--duration', recording_info['Time Limit'],
            '--frames', recording_info['Frame Limit']
        ]
        if recording_info['Point Filtering'] == False:
            command.append('--keep-invalid-points')
        recording_info['Subprocess']=util.run_command_as_subprosses(command=command)
    elif choice == 'Stop Recording':
        util.stop_subprosses(recording_info['Subprocess'])
        recording_info['Subprocess'] = 'Not Created'
    if choice == 'Back':
        extended_options()
    else:
        recording_options()

def utilities():
    utility_info = {
        'Point Filtering': False,
        'Output Path': 'my_recording.bin',
        'Time Limit': '0',
        'Frame Limit': '10',
        'Subprocess': 'Not Created'
    }
    update_status()
    options = [
        'Upload Device Configuration',
        'Upload Calibration',
        'Upload Calibration - Force Overwrite',
        'Update Firmware',
        ['Change IP', '| Changes IP reference, not IP on device'],
        'Set Output Path',
        'Start Recording',
        'Stop Recording',
        'Back'
    ]
    util.render_info(info=info, clear=True, title='Lidar Information and Status')
    util.render_info(info=status,colorize=True)
    # util.render_info(info=recording_info)
    choice = util.render_menu(options=options, title="Streaming Options Menu", warning="No action protection in this menu. If command contradicts with current lidar state or will cause a crash, program will execute anyway.")
    if choice == 'Upload Device Configuration':
        path = input('Please enter the path to the config file. To cancel, enter 0: ')
        if path != '0':
            util.run_command(f'voyant_lidar_client --url http://{info["Lidar IP Address"]}:8080 --endpoint config --file {path}')
    elif choice == 'Upload Calibration':
        path = input('Please enter the path to the calibration file. To cancel, enter 0: ')
        if path != '0':
            util.run_command(f'voyant_lidar_client --url http://{info["Lidar IP Address"]}:8080 --endpoint calibration --file {path}')
    elif choice == 'Upload Calibration - Force Overwrite':
        path = input('Please enter the path to the calibration file. To cancel, enter 0: ')
        if path != '0':
            util.run_command(f'voyant_lidar_client --url http://{info["Lidar IP Address"]}:8080 --endpoint calibration --file {path} --force-overwrite')
    elif choice == 'Update Firmware':
        path = input('Please enter the path to the firmware file. To cancel, enter 0: ')
        if path != '0':
            util.run_command(f'voyant_lidar_client --url http://{info["Lidar IP Address"]}:8080 --endpoint update --file {path}')
    if choice == 'Back':
        extended_options()
    else:
        playback()

try:
    home()
except Exception as e:
    cleanup()
    raise
