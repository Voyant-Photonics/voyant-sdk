#include <chrono>
#include <iostream>
#include <thread>
#include <voyant_client.hpp>

int main()
{
  std::cout << "Starting VoyantClient example..." << std::endl;

  // Set up signal handling
  VoyantClient::setupSignalHandling();

  // Create a multicast client (default connection type)
  VoyantClient client("0.0.0.0:4444", "224.0.0.0", "127.0.0.1");

  if(!client.isValid())
  {
    std::cerr << "Failed to create VoyantClient" << std::endl;
    return 1;
  }

  // Main loop
  std::cout << "Listening for frames (press Ctrl+C to exit)..." << std::endl;

  while(!VoyantClient::isTerminated())
  {
    // Check for new frame (returns nullptr if no new frame)
    const VoyantFrameWrapper *frame = client.update();

    if(frame)
    {
      std::cout << "###############" << std::endl;
      std::cout << "Received frame:" << std::endl;
      std::cout << *frame << std::endl;
    }

    // Sleep to avoid busy-waiting
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  return 0;
}
