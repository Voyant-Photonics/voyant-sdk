#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Dump the raw peak stream to a CSV file while the point cloud keeps streaming.

The dump runs on its own writer thread, so the point cloud is unaffected — this
example keeps draining frames the whole time. The dump ends when --max-frames
(or --max-peaks) is reached, or when stopped on Ctrl+C.

Example usage:
    python peak_dump_example.py peaks.csv
    python peak_dump_example.py peaks.csv --max-frames 100 --add-timestamp
"""

import argparse
import time

from voyant_api import CarbonClient, CarbonConfig, init_voyant_logging


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dump the raw peak stream to CSV while streaming",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="PATH",
        help="Output CSV path for the peak dump.",
    )
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help="Path to a JSON device config (e.g. config/device_config.json with your sensor interface_addr). If omitted, default CarbonConfig values are used.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        metavar="N",
        help="Stop the dump after N whole frames. Unbounded if omitted.",
    )
    parser.add_argument(
        "--max-peaks",
        type=int,
        default=None,
        metavar="N",
        help="Stop the dump after N CSV rows. Unbounded if omitted.",
    )
    parser.add_argument(
        "--add-timestamp",
        action="store_true",
        help="Insert a timestamp into the output filename.",
    )
    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()
    client = CarbonClient(config)
    client.start()
    print("CarbonClient started.")

    try:
        # A dump only receives data while the pipeline is running. Wait for the
        # first heartbeat so the sensor is actually streaming before we begin.
        client.wait_for_heartbeat()

        client.start_peak_dump(
            args.output,
            max_frames=args.max_frames,
            max_peaks=args.max_peaks,
            add_timestamp=args.add_timestamp,
        )
        # With --add-timestamp the writer inserts a timestamp into the filename,
        # so the final path differs from args.output.
        dest = f"{args.output} (timestamped)" if args.add_timestamp else args.output
        print(f"Peak dump started → {dest} (Ctrl+C to stop early)")

        # Keep draining frames so the point cloud keeps flowing during the dump.
        frame_count = 0
        while client.is_running() and client.is_peak_dumping():
            frame = client.try_receive_frame()
            if frame is not None:
                frame_count += 1
                print(f"Frame {frame_count}: {frame}")
            else:
                time.sleep(0.001)

        print(f"Peak dump finished after {frame_count} frames.")
    except KeyboardInterrupt:
        print("\nStopping peak dump...")
        # The interrupt may arrive before the dump starts (e.g. during
        # wait_for_heartbeat), so only stop a dump that is actually running.
        if client.is_peak_dumping():
            client.stop_peak_dump()
            # The file ends on a whole frame; poll until the writer is done.
            while client.is_peak_dumping():
                time.sleep(0.01)
        print("Peak dump stopped.")
    except RuntimeError as exc:
        print(f"Peak dump failed: {exc}")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
