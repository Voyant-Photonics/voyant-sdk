// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

/**
 * Send an SDL command to a Carbon sensor and wait for confirmation.
 *
 * SDL (Software Defined Lidar) commands configure the sensor at runtime —
 * changing operating state, field of view, frame rate, and waveform parameters.
 *
 * This example uses the recommended blocking SDL path. The client waits for a
 * heartbeat, builds the command from the current sensor read back, and calls
 * sendSdlBlocking() to apply the settings and wait for confirmation.
 */

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <cstring>
#include <exception>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <thread>

namespace
{
bool waitForHeartbeat(CarbonClient& client, SensorState& state, std::chrono::seconds timeout = std::chrono::seconds(5))
{
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (client.isRunning() && !CarbonClient::isTerminated() && std::chrono::steady_clock::now() < deadline)
    {
        state = client.getSensorState();
        if (state.last_heartbeat_frame > 0)
        {
            return true;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return false;
}

SdlCommandParams buildCommand(const SensorState& state)
{
    SdlCommandParams cmd   = toSdlCommand(state);
    cmd.req_state          = static_cast<uint8_t>(SdlState::PointCloud);
    cmd.hfov_deg           = 60.0f;
    cmd.hfov_center_deg    = 0.0f;
    cmd.frame_rate_fps     = 10.0f;
    cmd.ramp_bandwidth_ghz = 6.0f;
    // ramp_length is firmware-fixed (16.384 µs) and readback-only; the build ignores it.
    // For a static line (linescan), use makeLinescanCommand() instead.
    return cmd;
}

/**
 * Example only: this is not the recommended path for sending SDL commands.
 *
 * Prefer sendSdlBlocking() for normal use; it sends the command and waits for
 * confirmation. The sendSdl()/pollSdl() APIs are non-blocking; keep this pattern
 * for event loops that must poll SDL progress alongside frame processing. sendSdl()
 * applies a PointCloud request via the same transparent two-step as the blocking
 * path, so pollSdl() must be driven to completion to confirm it.
 */
SdlStatus nonBlockingSendAndPollExample(CarbonClient& client, const SdlCommandParams& cmd)
{
    SdlStatus status = client.sendSdl(cmd);
    if (status != SdlStatus::Pending)
    {
        return status;
    }

    while (client.isRunning() && !CarbonClient::isTerminated())
    {
        if (client.tryReceiveFrame())
        {
            // Do regular frame processing here.
            std::cout << "Frame: " << client.latestFrame() << std::endl;
        }

        status = client.pollSdl();
        if (status != SdlStatus::Pending)
        {
            return status;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    return SdlStatus::Pending;
}
} // namespace

int main(int argc, char** argv)
{
    voyant_log_init_c();
    CarbonClient::setupSignalHandling();

    // Connect to a real sensor by default; pass --sim to target a local carbon_simulator.
    bool sim = false;
    for (int i = 1; i < argc; ++i)
    {
        if (std::strcmp(argv[i], "--sim") == 0)
        {
            sim = true;
        }
    }

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

    SensorState state{};
    if (!waitForHeartbeat(client, state))
    {
        std::cerr << "Timed out waiting for a sensor heartbeat; cannot send SDL command." << std::endl;
        client.stop();
        return 1;
    }

    SdlCommandParams cmd{};
    try
    {
        cmd = buildCommand(state);
    }
    catch (const std::exception& e)
    {
        std::cerr << "Could not build SDL command from sensor state: " << e.what() << std::endl;
        client.stop();
        return 1;
    }

    std::cout << "Sending SDL command..." << std::endl;
    SdlStatus status = client.sendSdlBlocking(cmd);
    if (status != SdlStatus::Applied)
    {
        std::cerr << "SDL command failed: SdlStatus(" << static_cast<int>(status) << ")" << std::endl;
        client.stop();
        return 1;
    }

    std::cout << "SDL command applied successfully." << std::endl;

    int frame_count = 0;
    while (client.isRunning() && !CarbonClient::isTerminated())
    {
        if (client.tryReceiveFrame())
        {
            frame_count++;
            std::cout << "Frame " << frame_count << ": " << client.latestFrame() << std::endl;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    client.stop();
    return 0;
}
