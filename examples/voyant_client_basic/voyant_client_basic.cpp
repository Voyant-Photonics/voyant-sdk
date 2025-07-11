// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#include <chrono>
#include <iostream>
#include <logging_utils.hpp>
#include <thread>
#include <voyant_client.hpp>

int main()
{
  // Initialize API internal logging
  voyant_log_init_c();

  std::cout << "Starting VoyantClient example..." << std::endl;

  // Set up signal handling
  VoyantClient::setupSignalHandling();

  // Create a multicast client (default connection type)
  // These are the standard parameters for connecting to an actual sensor:
  // - "0.0.0.0:4444": Binds to all interfaces on port 4444
  // - "224.0.0.0": Standard multicast group address for the sensor
  // - "192.168.20.100": Your network interface's IP address
  //
  // For local testing in loopback mode, change these parameters:
  // VoyantClient client("0.0.0.0:4444", "224.0.0.0", "127.0.0.1");
  //  where:
  //  - "127.0.0.1": Interface address (localhost/loopback)
  VoyantClient client("0.0.0.0:4444", "224.0.0.0", "192.168.20.100");

  if(!client.isValid())
  {
    std::cerr << "Failed to create VoyantClient" << std::endl;
    return 1;
  }

  // Main loop
  std::cout << "Listening for frames (press Ctrl+C to exit)..." << std::endl;

  while(!VoyantClient::isTerminated())
  {
    if(client.tryReceiveNextFrame())
    {
      // Access latest frame as a mutable reference
      VoyantFrameWrapper &frame = client.latestFrame();

      std::cout << "###############" << std::endl;
      std::cout << "Received frame:" << std::endl;
      std::cout << frame << std::endl;
    }

    // Sleep to avoid busy-waiting
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  return 0;
}
