// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

/**
 * Dump the raw peak stream to a CSV file while the point cloud keeps streaming.
 *
 * The dump runs on its own writer thread, so the point cloud is unaffected —
 * this example keeps draining frames the whole time. The dump ends when
 * --max-frames is reached, or when stopped via Ctrl+C.
 *
 * Usage:
 *   peak_dump <output.csv> [--max-frames N] [--sim]
 */

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <sensor_state_display.hpp>
#include <thread>

int main(int argc, char **argv)
{
  voyant_log_init_c();
  CarbonClient::setupSignalHandling();

  if(argc < 2)
  {
    std::cerr << "Usage: " << argv[0] << " <output.csv> [--max-frames N] [--sim]" << std::endl;
    return 1;
  }
  const std::string output = argv[1];
  uint64_t maxFrames = 0; // 0 = unbounded
  bool sim = false;       // --sim targets a local carbon_simulator
  for(int i = 2; i < argc; ++i)
  {
    if(std::strcmp(argv[i], "--max-frames") == 0 && i + 1 < argc)
    {
      maxFrames = std::strtoull(argv[++i], nullptr, 10);
    }
    else if(std::strcmp(argv[i], "--sim") == 0)
    {
      sim = true;
    }
  }

  // Defaults target a real sensor; pass --sim to target a local carbon_simulator.
  CarbonConfig config;
  config.setBindAddr("0.0.0.0:5678").setGroupAddr("239.255.48.84");
  if(sim)
  {
    config.setInterfaceAddr("127.0.0.1").setFpgaTargetAddr("127.0.0.1:1234");
  }
  else
  {
    config.setInterfaceAddr("192.168.1.100").setFpgaTargetAddr("192.168.1.128:1234");
  }

  CarbonClient client(config);
  if(!client.start())
  {
    std::cerr << "Failed to start CarbonClient" << std::endl;
    return 1;
  }

  // A dump only receives data while the pipeline is running. Wait for the
  // first heartbeat so the sensor is actually streaming before we begin.
  if(!client.waitForHeartbeat())
  {
    std::cerr << "Timed out waiting for a sensor heartbeat." << std::endl;
    client.stop();
    return 1;
  }

  if(!client.startPeakDump(output, maxFrames))
  {
    std::cerr << "Failed to start peak dump (client not running, or a dump is already in progress)."
              << std::endl;
    client.stop();
    return 1;
  }
  std::cout << "Peak dump started -> " << output << " (Ctrl+C to stop early)" << std::endl;

  // Keep draining frames so the point cloud keeps flowing during the dump.
  while(client.isRunning() && client.isPeakDumping() && !CarbonClient::isTerminated())
  {
    if(client.tryReceiveFrame())
    {
      std::cout << "###############" << std::endl;
      std::cout << client.latestFrame() << std::endl;
      std::cout << "Sensor State: " << client.getSensorState() << std::endl;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  // If interrupted, ask the writer to finish on a whole frame and wait it out.
  if(client.isPeakDumping())
  {
    std::cout << "\nStopping peak dump..." << std::endl;
    client.stopPeakDump();
    while(client.isPeakDumping())
    {
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
  }

  std::cout << "Peak dump finished." << std::endl;
  client.stop();
  return 0;
}
