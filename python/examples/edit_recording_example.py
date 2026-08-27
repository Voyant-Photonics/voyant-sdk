#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Edit a Voyant recording and save it back: read each frame, filter/modify its
points as a numpy matrix, rebuild the frame with with_points(), and record the
result to a new .vynt file.

with_points() returns a new frame that keeps everything else from the frame it
came from — state snapshots, timestamps, frame index, device identity — so the
output recording plays back like the input with only its points changed. The
input file is read-only throughout; the edits land in a new file.

The same flow works on live frames from a CarbonClient — filter or annotate each
frame as it arrives, then record it.

Example usage:
    python edit_recording_example.py --input recording.vynt --output edited.vynt
    python edit_recording_example.py --input recording.vynt --output edited.vynt --max-range 25
"""

import argparse

from voyant_api import (
    RecordStatus,
    VoyantFrame,
    VoyantPlayback,
    VoyantRecorder,
    init_voyant_logging,
)

COLS = VoyantFrame.points_columns()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter a Voyant recording and save the result to a new file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the source recording (.vynt; convert a pre-v1.0.0 "
        "recording with voyant_recording_migrate first)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path for the edited recording (.vynt)",
    )
    parser.add_argument(
        "--max-range",
        type=float,
        default=50.0,
        help="Drop points farther than this range in meters",
    )
    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    # keep_invalid_points=False drops invalid returns as the frames are read, so the
    # output holds only valid points. Pass True to carry them through as well.
    playback = VoyantPlayback(keep_invalid_points=False)
    playback.open(args.input)

    with VoyantRecorder(args.output, timestamp_filename=False) as recorder:
        for frame in playback:
            if frame is None:
                break

            matrix = frame.points()

            # Any numpy edit works here. This one keeps near points and stamps
            # the user-owned column to mark the rows this script touched.
            keep = matrix[:, COLS.index("range_m")] <= args.max_range
            matrix = matrix[keep]
            matrix[:, COLS.index("user_data")] = 1

            # From a pandas DataFrame instead, select columns by name so column
            # order can't drift:
            #   matrix = df[VoyantFrame.points_columns()].to_numpy()

            edited = frame.with_points(matrix)
            if recorder.record_frame(edited) == RecordStatus.STOP:
                break

            print(
                f"frame {edited.frame_index}: kept "
                f"{edited.n_points}/{frame.n_points} points"
            )


if __name__ == "__main__":
    main()
