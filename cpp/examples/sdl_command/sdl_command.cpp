// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

/**
 * Send an SDL command to a Carbon sensor and wait for confirmation.
 *
 * SDL (Sensor Device Language) commands configure the sensor at runtime —
 * changing operating state, field of view, frame rate, and waveform parameters.
 *
 * This example sends a single command and polls for confirmation inline with
 * the frame receive loop.
 */

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <thread>

int main()
{
  voyant_log_init_c();
  CarbonClient::setupSignalHandling();

  CarbonConfig config;
  // Configure the client with the appropriate UDP addresses for the simulator
  config.setBindAddr("0.0.0.0:5678")
      .setGroupAddr("224.0.0.0")
      .setInterfaceAddr("127.0.0.1")
      .setFpgaTargetAddr("127.0.0.1:1234");

  CarbonClient client(config);
  if(!client.start())
  {
    std::cerr << "Failed to start CarbonClient" << std::endl;
    return 1;
  }

  // Build an SDL command — construct with defaults, override only what you need.
  SdlCommandParams cmd{};
  cmd.req_state = static_cast<uint8_t>(SdlState::PointCloud);
  cmd.hfov_deg = 60.0f;
  cmd.hfov_center_deg = 0.0f;
  cmd.frame_rate_fps = 10.0f;
  cmd.ramp_length = static_cast<uint8_t>(SdlRampLength::V16_384us);
  cmd.ramp_bandwidth_ghz = 6.0f;

  // Send — returns immediately.
  SdlStatus status = client.sendSdl(cmd);
  if(status != SdlStatus::Pending)
  {
    std::cerr << "SDL command rejected before sending: SdlStatus(" << static_cast<int>(status)
              << ")" << std::endl;
    client.stop();
    return 1;
  }

  std::cout << "SDL command sent. Waiting for confirmation..." << std::endl;

  int frame_count = 0;
  while(client.isRunning() && !CarbonClient::isTerminated())
  {
    if(client.tryReceiveFrame())
    {
      frame_count++;
      std::cout << "Frame " << frame_count << ": " << client.latestFrame() << std::endl;
    }

    // Poll for SDL confirmation on every iteration — the sensor confirms
    // via heartbeat, not frame data.
    status = client.pollSdl();
    if(status == SdlStatus::Applied)
    {
      std::cout << "SDL command applied successfully." << std::endl;
      break;
    }
    else if(status != SdlStatus::Pending)
    {
      std::cerr << "SDL command failed: SdlStatus(" << static_cast<int>(status) << ")" << std::endl;
      break;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  client.stop();
  return 0;
}
