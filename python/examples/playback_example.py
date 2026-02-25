#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Script to process Voyant recording files frame by frame.
Prints frame information and XYZ point cloud data as pandas DataFrames.
"""

import argparse
from voyant_api import VoyantPlayback
from voyant_api import init_voyant_logging
from voyant_api.utils import frame_to_dataframe


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process Voyant recording files frame by frame",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required argument
    parser.add_argument(
        "--input", help="Path to the Voyant recording file (.bin)", required=True
    )

    # Optional arguments with defaults matching the Rust code
    parser.add_argument(
        "--rate",
        type=float,
        default=None,
        help="Playback rate (1.0 = real-time, None = as fast as possible)",
    )

    parser.add_argument(
        "--loopback",
        action="store_true",
        default=False,
        help="Whether to loop when reaching the end of file",
    )

    parser.add_argument(
        "--keep-invalid-points",
        action="store_true",
        default=False,
        help="Keep invalid points (disable filtering)",
    )

    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    # Create VoyantPlayback instance
    playback = VoyantPlayback(
        rate=args.rate,
        loopback=args.loopback,
        filter_points=not args.keep_invalid_points,
    )

    # Open the input file
    playback.open(args.input)

    # Process frames
    for frame in playback:
        if frame is None:
            break

        print("\n#############")
        print(frame)
        df = frame_to_dataframe(frame)
        print(df)


if __name__ == "__main__":
    main()
