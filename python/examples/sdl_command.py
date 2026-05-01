#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Send an SDL command to a Carbon sensor and wait for confirmation.

SDL (Sensor Device Language) commands configure the sensor at runtime —
changing operating state, field of view, frame rate, and waveform parameters.

This example sends a single command and polls for confirmation inline with
the frame receive loop. In production, you may want to manage SDL in a
separate thread, especially if frame processing is time-sensitive.
"""

import argparse
import time
from voyant_api import (
    CarbonClient,
    CarbonConfig,
    SdlCommand,
    SdlState,
    SdlRampLength,
    SdlStatus,
    init_voyant_logging,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Send an SDL command to a Carbon sensor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help="Path to JSON config file. If omitted, default CarbonConfig values are used.",
    )
    parser.add_argument(
        "--hfov",
        type=float,
        default=60.0,
        metavar="DEG",
        help="Horizontal FOV in degrees (0.0 – 120.0).",
    )
    parser.add_argument(
        "--hfov-center",
        type=float,
        default=0.0,
        metavar="DEG",
        help="Horizontal FOV center in degrees (−60.0 – 60.0).",
    )
    parser.add_argument(
        "--frame-rate",
        type=float,
        default=10.0,
        metavar="FPS",
        help="Frame rate in fps (1.0 – 19.0).",
    )
    return parser.parse_args()


def build_command(args) -> SdlCommand:
    """Build an SdlCommand from command-line arguments."""
    cmd = SdlCommand()
    cmd.req_state = SdlState.PointCloud
    cmd.hfov_deg = args.hfov
    cmd.hfov_center_deg = args.hfov_center
    cmd.frame_rate_fps = args.frame_rate
    cmd.ramp_length = SdlRampLength.V16_384us
    return cmd


def main():
    init_voyant_logging()
    args = parse_args()

    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()

    client = CarbonClient(config)
    client.start()
    print("CarbonClient started. Press Ctrl+C to stop.\n")

    # Build and send the SDL command.
    cmd = build_command(args)
    print(f"Sending SDL command: {cmd}")
    status = client.send_sdl(cmd)

    if status != SdlStatus.Pending:
        # Command was rejected before sending — no need to poll.
        print(f"SDL command rejected: {status}")
        client.stop()
        return

    print("SDL command sent. Waiting for sensor confirmation...\n")
    sdl_resolved = False
    frame_count = 0

    try:
        while client.is_running():
            frame = client.try_receive_frame()

            if frame is not None:
                frame_count += 1
                print(f"Frame {frame_count}: {frame.n_valid_points} points")

            # Poll for SDL confirmation on every iteration, whether or not
            # a frame arrived. The sensor confirms via heartbeat, not frame data.
            if not sdl_resolved:
                status = client.poll_sdl()
                if status != SdlStatus.Pending:
                    sdl_resolved = True
                    if status == SdlStatus.Applied:
                        print("\nSDL command applied successfully.")
                    else:
                        print(f"\nSDL command failed: {status}")
                    break  # Stop after SDL is resolved — no need to poll further.

            if frame is None:
                time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\nReceived {frame_count} frames total.")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
