#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Receive live Voyant data and record it to a binary file.
"""

import argparse
import time
from voyant_api import CarbonClient, CarbonConfig
from voyant_api import VoyantRecorder
from voyant_api import RecordStatus
from voyant_api import init_voyant_logging


def parse_args():
    """Parse command-line arguments for the recording script."""
    parser = argparse.ArgumentParser(
        description="Receive and record live Voyant data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # --- Required Arguments ---
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Base path for the output recording file (.bin)",
    )

    # --- Network Configuration ---
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help=(
            "Path to JSON config file. "
            "If omitted, default CarbonConfig values are used."
        ),
    )

    # --- Recording Configuration ---
    parser.add_argument(
        "--frames-per-file",
        type=int,
        default=None,
        help="Maximum frames per file before splitting (None = no limit)",
    )
    parser.add_argument(
        "--duration-per-file",
        type=int,
        default=None,
        help="Maximum seconds per file before splitting (None = no limit)",
    )
    parser.add_argument(
        "--size-per-file-mb",
        type=int,
        default=None,
        help="Maximum MB per file before splitting (None = no limit)",
    )
    parser.add_argument(
        "--max-total-frames",
        type=int,
        default=None,
        help="Maximum total frames across all files (None = no limit)",
    )
    parser.add_argument(
        "--max-total-duration",
        type=int,
        default=None,
        help="Maximum total seconds across all files (None = no limit)",
    )
    parser.add_argument(
        "--max-total-size-mb",
        type=int,
        default=None,
        help="Maximum total MB across all files (None = no limit)",
    )
    parser.add_argument(
        "--no-timestamp-filename",
        dest="timestamp_filename",
        action="store_false",
        help="If set, disables adding a timestamp to the output filename",
    )

    # Set default for timestamp_filename to True, action='store_false' makes it False when flag is present
    parser.set_defaults(timestamp_filename=True)

    return parser.parse_args()


def main():
    """Main function to set up client and recorder and run the recording loop."""
    init_voyant_logging()

    args = parse_args()

    # 1. Create the client to receive frames from the network
    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()
    print("Using config:")
    print(config)
    print()

    client = CarbonClient(config)
    client.start()

    # 2. Create the recorder to write frames to a file
    recorder = VoyantRecorder(
        output_path=args.output,
        timestamp_filename=args.timestamp_filename,
        frames_per_file=args.frames_per_file,
        duration_per_file=args.duration_per_file,
        size_per_file_mb=args.size_per_file_mb,
        max_total_frames=args.max_total_frames,
        max_total_duration=args.max_total_duration,
        max_total_size_mb=args.max_total_size_mb,
    )

    print(f"Recording to '{args.output}'. Press Ctrl+C to stop.")

    try:
        # 3. Run the main recording loop
        while client.is_running():
            frame = client.try_receive_frame()
            if frame is not None:
                ###############################################
                # Insert your point cloud processing magic here
                ###############################################

                # NOTE: Python-based recording may struggle to keep up with high-frequency
                # data streams. If you experience frame drops, consider using the native
                # binary recorder for more reliable capture.
                status = recorder.record_frame(frame)

                if status == RecordStatus.STOP:
                    print("\nRecording limit reached. Finalizing...")
                    break  # Stop the loop as the recording limit was hit

                elif status == RecordStatus.SPLIT:
                    print("File split due to limit")  # Log that a new file was created

                elif status != RecordStatus.OK:
                    print("Error recording frame")
                    break

                # Periodically print progress for "ok" and "split" statuses
                total = recorder.frames_recorded
                if total > 0 and total % 100 == 0:
                    print(f"Recorded {total} frames in {recorder.split_count} files...")

            else:
                # No frame available yet, sleep briefly to avoid a busy loop
                time.sleep(0.001)

    except KeyboardInterrupt:
        print("\nCtrl+C detected. Finalizing recording...")
    finally:
        client.stop()

        # 4. Finalize the recording to ensure the file is properly closed
        if recorder:
            print(f"Finalizing recording after {recorder.frames_recorded} total frames")
            recorder.finalize()
            print("Recording finalized")


if __name__ == "__main__":
    main()
