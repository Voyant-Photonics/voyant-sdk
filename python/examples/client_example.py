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
from voyant_api import VoyantClient
from voyant_api import init_voyant_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="Receive live Voyant data over multicast UDP",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--bind-addr",
        type=str,
        default="0.0.0.0:4444",
        help="Local socket address to bind to",
    )

    parser.add_argument(
        "--group-addr",
        type=str,
        default="224.0.0.0",
        help="Multicast group address",
    )

    parser.add_argument(
        "--interface-addr",
        type=str,
        default="127.0.0.1",
        help="Interface address for multicast",
    )

    parser.add_argument(
        "--keep-invalid-points",
        action="store_true",
        default=False,
        help="Whether to filter out invalid points",
    )

    parser.add_argument(
        "--use-msg-stamps",
        action="store_true",
        default=False,
        help=(
            "Use timestamps from received point groups instead of system time. "
            "WARNING: Do not use this flag with Carbon Dev Kit (Meadowlark) units!"
        ),
    )

    parser.add_argument(
        "--track-timing",
        action="store_true",
        default=False,
        help="Whether to collect statistics on packet timing and latency",
    )

    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    print(f"Starting Voyant client on {args.interface_addr}")
    print("Press Ctrl+C to stop\n")

    # Create client
    client = VoyantClient(
        bind_addr=args.bind_addr,
        group_addr=args.group_addr,
        interface_addr=args.interface_addr,
        filter_points=not args.keep_invalid_points,
        use_msg_stamps=args.use_msg_stamps,
        track_timing=args.track_timing,
    )

    frame_count = 0

    try:
        while True:
            frame = client.try_receive_frame()

            if frame:
                frame_count += 1
                print(f"Frame {frame_count}: {frame}")

                # Get XYZ data as numpy array
                xyzv = frame.xyzv()
                print(f"xyzv data:\n{xyzv}\n")
                print()
            else:
                # No frame available
                pass

            # Sleep briefly to avoid busy loop
            time.sleep(0.01)

    except KeyboardInterrupt:
        print(f"\nReceived {frame_count} frames")


if __name__ == "__main__":
    main()
