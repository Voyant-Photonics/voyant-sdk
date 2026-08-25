#!/usr/bin/env python3
# Copyright (c) 2024-2025 Voyant Photonics, Inc.
#
# This example code is licensed under the MIT License.
# See the LICENSE file in the repository root for full license text.

"""
Record a diagnostic support bundle: a frame recording plus the raw-peaks sidecar.

Diagnostic mode keeps invalid points (with their drop reasons) in the frames, and
start_diagnostic_capture() writes the raw peak stream to a sidecar log alongside
them — together the two files form the bundle Voyant support asks for.

Example usage:
    python diagnostic_capture_example.py my_recording.vynt
    python diagnostic_capture_example.py my_recording.vynt --max-frames 100
"""

import argparse
import sys
import time
from pathlib import Path

from voyant_api import (
    CarbonClient,
    CarbonConfig,
    RecordStatus,
    VoyantRecorder,
    init_voyant_logging,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Record frames plus the raw-peaks sidecar for Voyant support",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "output",
        type=str,
        metavar="PATH",
        help="Output .vynt path for the frame recording; the peaks sidecar is "
        "written next to it as <name>_peaks.vynt.",
    )
    parser.add_argument(
        "--config",
        type=str,
        metavar="PATH",
        help=(
            "Path to a JSON device config (e.g. config/device_config.json "
            "with your sensor interface_addr). "
            "If omitted, default CarbonConfig values are used."
        ),
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        metavar="N",
        help="Stop after recording N frames. Unbounded if omitted (Ctrl+C to stop).",
    )
    return parser.parse_args()


def main():
    init_voyant_logging()
    args = parse_args()

    config = CarbonConfig.from_json(args.config) if args.config else CarbonConfig()
    # Diagnostic capture requires diagnostic mode, set before the client starts.
    config.set_diagnostic_mode(True)
    client = CarbonClient(config)
    client.start()
    print("CarbonClient started (diagnostic mode).")

    output = Path(args.output)
    # Assigned once the recorder resolves its timestamped name; the final report reads
    # them after the recorder's scope has closed.
    recorded = None
    sidecar = None
    exit_code = 0

    try:
        # The capture only receives data while the pipeline is running. Wait for
        # the first heartbeat so the sensor is actually streaming before we begin.
        client.wait_for_heartbeat()

        with VoyantRecorder(str(output)) as recorder:
            # Timestamp naming is on by default, so the resolved path is the only way to
            # name a sidecar that pairs with the recording.
            recorded = Path(recorder.current_file_path)
            sidecar = recorded.with_name(f"{recorded.stem}_peaks.vynt")
            # Started only once the recording file is open, so a refused recording
            # path cannot leave an orphan sidecar behind.
            client.start_diagnostic_capture(str(sidecar))
            print(f"Diagnostic capture started -> {sidecar}")
            print(f"Recording frames -> {recorded} (Ctrl+C to stop)")
            frame_count = 0
            # Caught inside the recorder's scope: Ctrl+C is the normal way to end an
            # unbounded run, so the bundle is complete and gets reported as such.
            try:
                # A writer that stops on its own ends the run: the bundle is already
                # incomplete. The finally block reports the reason.
                while client.is_running() and client.is_diagnostic_capturing():
                    frame = client.try_receive_frame()
                    if frame is None:
                        time.sleep(0.001)
                        continue
                    status = recorder.record_frame(frame)
                    frame_count += 1
                    if status == RecordStatus.STOP:
                        break
                    if args.max_frames is not None and frame_count >= args.max_frames:
                        break
            except KeyboardInterrupt:
                print("\nStopping...")
            print(f"Recorded {frame_count} frames.")
    except KeyboardInterrupt:
        # Reached only before the capture started; nothing was written.
        print("\nStopping...")
        exit_code = 1
    except (OSError, RuntimeError) as exc:
        # A refused recording path (or a failed frame write) raises OSError; a refused
        # sidecar, RuntimeError.
        print(f"Support bundle not written: {exc}")
        exit_code = 1
    finally:
        # The sidecar ends on a whole frame; poll until the writer is done.
        if client.is_diagnostic_capturing():
            client.stop_diagnostic_capture()
            while client.is_diagnostic_capturing():
                time.sleep(0.01)
        if error := client.diagnostic_capture_error():
            print(f"Sidecar capture ended with an error: {error}")
            exit_code = 1
        client.stop()

    # Announced only here: the sidecar is finalized and checked by now, so a
    # half-written bundle can't be reported as a good one.
    if exit_code == 0:
        print(f"Support bundle: {recorded} + {sidecar}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
