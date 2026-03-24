// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

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
  config.setBindAddr("0.0.0.0:5678").setGroupAddr("224.0.0.0").setInterfaceAddr("127.0.0.1");

  // Optional: override defaults as needed
  // config.setRangeMax(50.0f);
  // config.setPfa(1e-4f);

  CarbonClient client(config);
  client.start();

  std::cout << "Listening for frames (Ctrl+C to exit)..." << std::endl;

  while(client.isRunning() && !CarbonClient::isTerminated())
  {
    if(client.tryReceiveFrame())
    {
      std::cout << "###############" << std::endl;
      std::cout << client.latestFrame() << std::endl;
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
  }

  client.stop();
  return 0;
}
