#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Convert a Voyant binary recording to per-frame PCD files.

Each frame is saved as <output_dir>/frame_<frame_index>.pcd

By default, only the first 100 frames are converted. Use --max-frames to
change this, or --min-frame-index / --max-frame-index to convert a specific
range by sensor frame index.

Note: Frame indices reflect sensor uptime and do not start from zero
per recording. Use --keep-invalid-points to include invalid points in
the converted PCD files.

Example usage:
    python pcd_conversion_example.py --input recording.bin --output-dir ./pcd_out
    python pcd_conversion_example.py --input recording.bin --output-dir ./pcd_out --max-frames 500
    python pcd_conversion_example.py --input recording.bin --output-dir ./pcd_out --min-frame-index 1000 --max-frame-index 1099
"""

import argparse
import os
from voyant_api import VoyantPlayback
from voyant_api import init_voyant_logging
from voyant_api.pcd_utils import save_frame_to_pcd

DEFAULT_MAX_FRAMES = 100


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a Voyant binary recording to per-frame PCD files",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the Voyant recording file (.bin)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Directory to write PCD files into (will be created if it does not exist)",
    )

    # Frame selection
    parser.add_argument(
        "--max-frames",
        type=int,
        default=DEFAULT_MAX_FRAMES,
        help=(
            "Maximum number of frames to convert. "
            f"Defaults to {DEFAULT_MAX_FRAMES} to avoid accidentally filling disk. "
            "Pass 0 for no limit."
        ),
    )
    parser.add_argument(
        "--min-frame-index",
        type=int,
        default=None,
        help="Only convert frames with a sensor frame index >= this value",
    )
    parser.add_argument(
        "--max-frame-index",
        type=int,
        default=None,
        help="Only convert frames with a sensor frame index <= this value",
    )

    # Point options
    parser.add_argument(
        "--keep-invalid-points",
        action="store_true",
        default=False,
        help="Include invalid points in converted PCD files",
    )
    parser.add_argument(
        "--base-fields-only",
        action="store_true",
        default=False,
        help=(
            "Write only base fields (x, y, z, radial_vel, snr_linear, "
            "nanosecs_since_frame, drop_reason) instead of all extended fields"
        ),
    )

    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    converted = 0
    skipped = 0
    max_frames = args.max_frames if args.max_frames > 0 else None

    with VoyantPlayback(
        filter_points=not args.keep_invalid_points,
    ) as playback:
        playback.open(args.input)

        for frame in playback:
            if frame is None:
                break

            frame_index = frame.frame_index

            # Apply sensor frame index range filter
            if args.min_frame_index is not None and frame_index < args.min_frame_index:
                skipped += 1
                continue
            if args.max_frame_index is not None and frame_index > args.max_frame_index:
                break

            # Apply conversion count limit
            if max_frames is not None and converted >= max_frames:
                print(
                    f"Reached --max-frames limit of {max_frames}. "
                    "Pass --max-frames 0 to convert all frames."
                )
                break

            pcd_path = os.path.join(args.output_dir, f"frame_{frame_index}.pcd")

            ###############################################
            # save_frame_to_pcd is a convenience wrapper around pcd_utils functions.
            # You can also use the individual conversions for other workflows, e.g.:
            #   pc = pcd_utils.frame_to_xyz_pcd(frame)       # xyz only
            #   pc = pcd_utils.frame_to_extended_pcd(frame)  # all fields
            #   pc.save(pcd_path)                             # save manually
            ###############################################
            save_frame_to_pcd(
                frame,
                pcd_path,
                valid_only=not args.keep_invalid_points,
                extended=not args.base_fields_only,
            )
            converted += 1

            if converted % 10 == 0:
                print(f"Converted {converted} frames...")

    print(f"\nDone. Converted {converted} frames to '{args.output_dir}'")
    if skipped:
        print(f"Skipped {skipped} frames before --min-frame-index")


if __name__ == "__main__":
    main()
