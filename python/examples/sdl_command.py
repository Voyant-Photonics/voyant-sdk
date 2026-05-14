#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Send an SDL command to a Carbon sensor and wait for confirmation.

SDL (Software Defined Lidar) commands configure the sensor at runtime —
changing operating state, field of view, frame rate, and waveform parameters.

This example uses the recommended blocking SDL path. The client waits for a
heartbeat, builds the command from the current sensor read back, and lets
send_sdl_blocking() apply settings through Idle and resume PointCloud
automatically.
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


def wait_for_heartbeat(client, timeout_sec=5.0):
    """Wait until sensor_state() contains heartbeat-derived SDL state."""
    deadline = time.monotonic() + timeout_sec
    while client.is_running() and time.monotonic() < deadline:
        state = client.sensor_state()
        if state.last_heartbeat_frame > 0:
            return state
        time.sleep(0.05)
    return None


def build_command(state, args) -> SdlCommand:
    """Build an SdlCommand by modifying the latest heartbeat read back."""
    cmd = state.to_sdl_command()
    cmd.req_state = SdlState.PointCloud
    cmd.hfov_deg = args.hfov
    cmd.hfov_center_deg = args.hfov_center
    cmd.frame_rate_fps = args.frame_rate
    cmd.ramp_length = SdlRampLength.V16_384us
    return cmd


def non_blocking_send_and_poll_example(client, cmd: SdlCommand) -> SdlStatus:
    """Example only: this is not the recommended path for sending SDL commands.

    Prefer send_sdl_blocking(), which applies settings through Idle and resumes
    PointCloud automatically unless the command requests Idle. The
    send_sdl()/poll_sdl() APIs are non-blocking; keep this pattern for event
    loops that must poll SDL progress alongside frame processing.
    """
    status = client.send_sdl(cmd)
    if status != SdlStatus.Pending:
        return status

    while client.is_running():
        frame = client.try_receive_frame()
        if frame is not None:
            # Do regular frame processing here.
            print(f"Frame: {frame.n_valid_points} points")

        status = client.poll_sdl()
        if status != SdlStatus.Pending:
            return status

        if frame is None:
            time.sleep(0.001)

    return SdlStatus.Pending


def main():
    init_voyant_logging()
    args = parse_args()

    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()

    client = CarbonClient(config)
    client.start()
    print("CarbonClient started. Press Ctrl+C to stop.\n")

    state = wait_for_heartbeat(client)
    if state is None:
        print("Timed out waiting for a sensor heartbeat; cannot send SDL command.")
        client.stop()
        return

    try:
        cmd = build_command(state, args)
    except ValueError as exc:
        print(f"Could not build SDL command from sensor state: {exc}")
        client.stop()
        return

    print(f"Sending SDL command: {cmd}")
    status = client.send_sdl_blocking(cmd)

    if status != SdlStatus.Applied:
        print(f"SDL command failed: {status}")
        client.stop()
        return

    print("SDL command applied successfully.\n")
    frame_count = 0

    try:
        while client.is_running():
            frame = client.try_receive_frame()

            if frame is not None:
                frame_count += 1
                print(f"Frame {frame_count}: {frame.n_valid_points} points")

            if frame is None:
                time.sleep(0.001)

    except KeyboardInterrupt:
        print(f"\nReceived {frame_count} frames total.")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
