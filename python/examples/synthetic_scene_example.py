#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Record a synthetic scene as a .vynt log: build each frame from a generated point
matrix with VoyantFrame.synthetic(), declare the scan configuration with
with_sdl(), and record the sequence — the output opens in the visualizer and
replays like any sensor recording, identified by its "SIM-SW" device id.

The scene here is deliberately simple — a wall of points on an equally spaced
azimuth/elevation grid whose range drifts over time. Swap generate_wall() for
your own generator (e.g. points sampled from a simulator scene) and keep the
rest of the loop as is.

Example usage:
    python synthetic_scene_example.py
    python synthetic_scene_example.py --output my_scene.vynt --frames 250
"""

import argparse
import math

import numpy as np
from voyant_api import (
    ProductId,
    RecordStatus,
    SdlCommand,
    SdlState,
    VoyantFrame,
    VoyantRecorder,
    init_voyant_logging,
)

COLS = VoyantFrame.points_columns()

# Scene geometry: an equally spaced angular grid, azimuth-fastest, with
# (azimuth_idx, elevation_idx) = (0, 0) at the top-left like a camera image.
ELEVATIONS = 16
AZIMUTHS = 128
HFOV_DEG = 90.0
VFOV_DEG = 20.0
FPS = 10.0


def generate_wall(frame_number: int) -> np.ndarray:
    """A wall of points in the points() column layout; range drifts per frame."""
    range_m = 10.0 + 2.0 * math.sin(2.0 * math.pi * frame_number / 50.0)

    elevation_idx, azimuth_idx = np.mgrid[0:ELEVATIONS, 0:AZIMUTHS]
    elevation_idx = elevation_idx.ravel().astype(np.float64)
    azimuth_idx = azimuth_idx.ravel().astype(np.float64)

    az_step = math.radians(HFOV_DEG) / (AZIMUTHS - 1)
    el_step = math.radians(VFOV_DEG) / (ELEVATIONS - 1)

    matrix = np.zeros((ELEVATIONS * AZIMUTHS, len(COLS)))
    matrix[:, COLS.index("range_m")] = range_m
    # Azimuth sweeps left to right; elevation descends so index 0 is the top line.
    matrix[:, COLS.index("azimuth_rad")] = (
        -math.radians(HFOV_DEG) / 2 + azimuth_idx * az_step
    )
    matrix[:, COLS.index("elevation_rad")] = (
        math.radians(VFOV_DEG) / 2 - elevation_idx * el_step
    )
    matrix[:, COLS.index("snr")] = 20.0
    matrix[:, COLS.index("azimuth_idx")] = azimuth_idx
    matrix[:, COLS.index("elevation_idx")] = elevation_idx
    matrix[:, COLS.index("drop_reason")] = 1  # valid
    return matrix


def main():
    parser = argparse.ArgumentParser(
        description="Record a synthetic scene as a .vynt log",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output", default="synthetic_scene.vynt", help="Output .vynt path"
    )
    parser.add_argument(
        "--frames", type=int, default=100, help="Number of frames to record"
    )
    args = parser.parse_args()
    # Upper bound matches frame_index's u32; without it the run raises mid-recording.
    if not 0 <= args.frames <= 0xFFFFFFFF:
        parser.error("--frames must be in 0..4294967295")

    init_voyant_logging()

    # The configuration the scene claims to have been generated under; replays as
    # applied sensor configuration (visible in the visualizer's state panels).
    sdl = SdlCommand()
    sdl.req_state = SdlState.PointCloud
    sdl.frame_rate_fps = FPS
    sdl.hfov_deg = HFOV_DEG

    start_seconds = 1_700_000_000
    frame_period_ns = round(1e9 / FPS)

    with VoyantRecorder(args.output, timestamp_filename=False) as recorder:
        for i in range(args.frames):
            total_ns = i * frame_period_ns
            frame = VoyantFrame.synthetic(
                generate_wall(i),
                source=ProductId.SoftwareSimulator,
                timestamp_seconds=start_seconds + total_ns // 1_000_000_000,
                timestamp_nanoseconds=total_ns % 1_000_000_000,
                frame_index=i,
            ).with_sdl(sdl)
            # No limits are configured, so SPLIT/STOP cannot occur — anything
            # but OK failed.
            if recorder.record_frame(frame) != RecordStatus.OK:
                raise SystemExit(f"Failed to record frame {i}")

    print(f"Recorded {args.frames} synthetic frames to {args.output}")
    print(f"View it by running: voyant_visualizer --input {args.output}")


if __name__ == "__main__":
    main()
