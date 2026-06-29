// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

/**
 * Calibrate a Carbon sensor's background-noise mask over the native API.
 *
 * Two operations, both of which require the sensor to be in Idle:
 *   - Apply Default: write the compiled-in default mask for the box (fast).
 *   - Refine (--refine): refine the mask from a covered-window capture. The
 *     sensor window MUST be covered first — the capture assumes background noise
 *     only. This cycles the sensor internally and returns it to Idle (~10-20 s).
 *
 * Both calls block until done. Unlike the visualizer, the bindings do not start
 * streaming afterward — the sensor is left in Idle. The box is identified from
 * the sensor's heartbeat — no serial argument needed.
 *
 * Usage:
 *   background_noise_calibration [--refine]
 */

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <cstring>
#include <iostream>
#include <logging_utils_ffi.hpp>

int main(int argc, char** argv)
{
    voyant_log_init_c();
    CarbonClient::setupSignalHandling();

    bool refine = false;
    bool sim    = false; // --sim targets a local carbon_simulator
    for (int i = 1; i < argc; ++i)
    {
        if (std::strcmp(argv[i], "--refine") == 0)
        {
            refine = true;
        }
        else if (std::strcmp(argv[i], "--sim") == 0)
        {
            sim = true;
        }
    }

    // Connect to a real sensor by default; pass --sim to target a local carbon_simulator.
    CarbonConfig config;
    if (sim)
    {
        // Point at the local carbon_simulator on loopback.
        config.setInterfaceAddr("127.0.0.1").setFpgaTargetAddr("127.0.0.1:1234");
    }
    CarbonClient client(config);
    if (!client.start())
    {
        std::cerr << "Failed to start CarbonClient" << std::endl;
        return 1;
    }

    // Both operations require a heartbeat (for the box serial) and Idle on entry.
    if (!client.waitForHeartbeat())
    {
        std::cerr << "Timed out waiting for a sensor heartbeat." << std::endl;
        client.stop();
        return 1;
    }

    if (!client.ensureIdleForCalibration())
    {
        std::cerr << "Could not drive the sensor to Idle; aborting." << std::endl;
        client.stop();
        return 1;
    }

    bool ok = false;
    if (refine)
    {
        std::cout << "Cover the sensor window now — refinement assumes background noise only. "
                     "Running refinement (~10-20 s)..."
                  << std::endl;
        ok = client.refineBackgroundNoise(); // 0 iterations → built-in default
        std::cout << (ok ? "Background-noise refinement complete." : "Background-noise refinement failed.") << std::endl;
    }
    else
    {
        ok = client.applyDefaultBackgroundNoise();
        std::cout << (ok ? "Default background-noise calibration applied." : "Default background-noise calibration failed.")
                  << std::endl;
    }

    client.stop();
    return ok ? 0 : 1;
}
