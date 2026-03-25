#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Receive live Voyant data over multicast UDP.
"""

import argparse
import time
from voyant_api import CarbonClient, CarbonConfig, init_voyant_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="Receive live Voyant data over multicast UDP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help=(
            "Path to JSON config file. "
            "If omitted, default CarbonConfig values are used."
        ),
    )

    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()
    print("Using config:")
    print(config)
    print()

    print("Starting CarbonClient...")
    print("Press Ctrl+C to stop\n")

    client = CarbonClient(config)
    client.start()
    frame_count = 0

    try:
        while client.is_running():
            frame = client.try_receive_frame()

            if frame is not None:
                frame_count += 1
                print(f"Frame {frame_count}: {frame}")

                # Get XYZ + radial velocity as numpy array
                xyzv = frame.xyzv()
                print(f"xyzv data:\n{xyzv}\n")
                print()

                ###############################################
                # Insert your point cloud processing magic here
                ###############################################

            else:
                # No frame available
                time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\nReceived {frame_count} frames")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
