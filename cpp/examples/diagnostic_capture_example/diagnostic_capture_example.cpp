// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

/**
 * Record a diagnostic support bundle: a frame recording plus the raw-peaks sidecar.
 *
 * Diagnostic mode keeps invalid points (with their drop reasons) in the frames, and
 * startDiagnosticCapture() writes the raw peak stream to a sidecar log alongside
 * them — together the two files form the bundle Voyant support asks for.
 *
 * Usage:
 *   diagnostic_capture_example <output.vynt> [--max-frames N] [--sim]
 */

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <string>
#include <thread>
#include <voyant_data_recorder.hpp>

int main(int argc, char** argv)
{
    voyant_log_init_c();
    CarbonClient::setupSignalHandling();

    if (argc < 2)
    {
        std::cerr << "Usage: " << argv[0] << " <output.vynt> [--max-frames N] [--sim]" << std::endl;
        return 1;
    }
    const std::string output    = argv[1];
    uint64_t          maxFrames = 0;     // 0 = unbounded
    bool              sim       = false; // --sim targets a local voyant_simulator
    for (int i = 2; i < argc; ++i)
    {
        if (std::strcmp(argv[i], "--max-frames") == 0 && i + 1 < argc)
        {
            maxFrames = std::strtoull(argv[++i], nullptr, 10);
        }
        else if (std::strcmp(argv[i], "--sim") == 0)
        {
            sim = true;
        }
    }

    // The sidecar is named after the recording so the two files pair up. Strip the
    // extension only at the end of the path — a directory name can contain it too.
    const std::string suffix = ".vynt";
    std::string       stem   = output;
    if (stem.size() > suffix.size() && stem.compare(stem.size() - suffix.size(), suffix.size(), suffix) == 0)
    {
        stem.resize(stem.size() - suffix.size());
    }
    const std::string sidecar = stem + "_peaks.vynt";

    // Connect to a real sensor by default; pass --sim to target a local voyant_simulator.
    CarbonConfig config;
    if (sim)
    {
        // Point at the local voyant_simulator on loopback.
        config.setInterfaceAddr("127.0.0.1").setFpgaTargetAddr("127.0.0.1:1234");
    }
    // Diagnostic capture requires diagnostic mode, set before the client starts.
    config.setDiagnosticMode(true);
    CarbonClient client(config);
    if (!client.start())
    {
        std::cerr << "Failed to start CarbonClient" << std::endl;
        return 1;
    }

    // The capture only receives data while the pipeline is running. Wait for the
    // first heartbeat so the sensor is actually streaming before we begin.
    if (!client.waitForHeartbeat())
    {
        std::cerr << "Timed out waiting for a sensor heartbeat." << std::endl;
        client.stop();
        return 1;
    }

    VoyantRecorderConfig recorderConfig(output);
    recorderConfig.timestampFilename = false;
    VoyantRecorder recorder(recorderConfig);
    if (!recorder.isValid())
    {
        std::cerr << "Failed to create VoyantRecorder for " << output << ": " << recorder.getLastError() << std::endl;
        client.stop();
        return 1;
    }
    std::cout << "Recording frames -> " << output << " (Ctrl+C to stop)" << std::endl;

    // Started only once the recording file is open, so a refused recording path
    // cannot leave an orphan sidecar behind.
    if (!client.startDiagnosticCapture(sidecar))
    {
        std::cerr << "Failed to start diagnostic capture (diagnostic_mode off, client not "
                     "running, a capture already in progress, or "
                  << sidecar << " already exists)." << std::endl;
        recorder.finalize();
        client.stop();
        return 1;
    }
    std::cout << "Diagnostic capture started -> " << sidecar << std::endl;

    uint64_t frameCount   = 0;
    bool     recordFailed = false;
    // A writer that stops on its own ends the run: the bundle is already incomplete.
    while (client.isRunning() && client.isDiagnosticCapturing() && !CarbonClient::isTerminated())
    {
        auto frame = client.tryReceiveFrame();
        if (!frame)
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
            continue;
        }
        const RecordResult result = recorder.recordFrame(*frame);
        if (result == RecordResult::Error || result == RecordResult::Unknown)
        {
            std::cerr << "Failed to record a frame — the bundle is incomplete." << std::endl;
            recordFailed = true;
            break;
        }
        ++frameCount;
        if (result == RecordResult::Finished || (maxFrames != 0 && frameCount >= maxFrames))
        {
            break;
        }
    }
    std::cout << "Recorded " << frameCount << " frames." << std::endl;
    if (!recorder.finalize())
    {
        std::cerr << "Failed to close the frame recording — the bundle is incomplete." << std::endl;
        recordFailed = true;
    }

    // The sidecar ends on a whole frame; ask the writer to finish and wait it out.
    if (client.isDiagnosticCapturing())
    {
        client.stopDiagnosticCapture();
        while (client.isDiagnosticCapturing())
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
    const std::string error = client.diagnosticCaptureError();
    if (!error.empty())
    {
        std::cerr << "Sidecar capture ended with an error: " << error << std::endl;
    }

    client.stop();
    // A half-written bundle must not report success — support would chase the wrong thing.
    if (recordFailed || !error.empty())
    {
        std::cerr << "Support bundle INCOMPLETE: " << output << " + " << sidecar << std::endl;
        return 1;
    }
    std::cout << "Support bundle: " << output << " + " << sidecar << std::endl;
    return 0;
}
