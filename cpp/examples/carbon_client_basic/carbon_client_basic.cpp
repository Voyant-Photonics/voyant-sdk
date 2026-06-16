// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <cstring>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <sensor_state_display.hpp>
#include <thread>

int main(int argc, char **argv)
{
  voyant_log_init_c();
  CarbonClient::setupSignalHandling();

  bool sim = false; // --sim targets a local carbon_simulator
  for(int i = 1; i < argc; ++i)
  {
    if(std::strcmp(argv[i], "--sim") == 0)
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

  // Optional: override defaults as needed
  // config.setRangeMax(50.0f);
  // config.setPfa(1e-4f);

  CarbonClient client(config);
  if(!client.start())
  {
    std::cerr << "Failed to start CarbonClient" << std::endl;
    return 1;
  }

  std::cout << "Listening for frames (Ctrl+C to exit)..." << std::endl;

  while(client.isRunning() && !CarbonClient::isTerminated())
  {
    if(client.tryReceiveFrame())
    {
      std::cout << "###############" << std::endl;
      std::cout << client.latestFrame() << std::endl;
      std::cout << "Sensor State: " << client.getSensorState() << std::endl;
      std::cout << "Time Sync: " << client.getTimeSyncState() << std::endl;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  client.stop();
  return 0;
}
