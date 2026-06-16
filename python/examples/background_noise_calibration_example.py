#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Calibrate a Carbon sensor's background-noise mask over the native API.

The box is identified from the sensor's heartbeat — no serial argument needed.
Two operations, both of which require the sensor to be in Idle:
  - Apply Default: write the compiled-in default mask for the box (fast).
  - Refine (--refine): refine the mask from a covered-window capture. The sensor
    window MUST be covered first — the capture assumes background noise only.
    This cycles the sensor internally and returns it to Idle (takes ~10-20 s).

Both calls block until done. Unlike the visualizer, the bindings do not start
streaming afterward — the sensor is left in Idle.

Example usage:
    python background_noise_calibration_example.py
    python background_noise_calibration_example.py --refine
"""

import argparse

from voyant_api import (
    CarbonClient,
    CarbonConfig,
    init_voyant_logging,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calibrate the Carbon background-noise mask",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help="Path to a JSON device config (e.g. config/device_config.json with your sensor interface_addr). If omitted, default CarbonConfig values are used.",
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="Refine the mask from a covered-window capture instead of writing the default.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        metavar="N",
        help="Refinement iterations (only with --refine). Defaults internally when omitted.",
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
        # Both operations require a heartbeat (for the box serial) and Idle on entry.
        client.wait_for_heartbeat()
        client.ensure_idle_for_calibration()

        if args.refine:
            print(
                "Cover the sensor window now — refinement assumes background noise only. "
                "Running refinement (~10-20 s)..."
            )
            client.refine_background_noise(args.iterations)
            print("Background-noise refinement complete.")
        else:
            client.apply_default_background_noise()
            print("Default background-noise calibration applied.")
    except RuntimeError as exc:
        print(f"Calibration failed: {exc}")
    finally:
        client.stop()


if __name__ == "__main__":
    main()
