// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#include <chrono>
#include <iomanip>
#include <iostream>
#include <string>
#include <voyant_playback.hpp>

void printUsage(const char *programName)
{
  std::cerr << "Usage: " << programName << " <recording_file_path> [playback_rate] [loop]" << std::endl;
  std::cerr << "  playback_rate: Optional, controls playback speed (default: real-time)" << std::endl;
  std::cerr << "                 0 for as-fast-as-possible" << std::endl;
  std::cerr << "                 1.0 for real-time" << std::endl;
  std::cerr << "                 2.0 for double speed, etc." << std::endl;
  std::cerr << "  loop:          Optional, 'loop' to enable looping (default: '')" << std::endl;
}

int main(int argc, char *argv[])
{
  // Check command line arguments
  if(argc < 2)
  {
    printUsage(argv[0]);
    return 1;
  }

  std::string filePath = argv[1];
  double playbackRate = 1.0; // Default to real-time
  bool looping = false;      // Default to no looping

  if(argc > 2)
  {
    try
    {
      playbackRate = std::stod(argv[2]);
    }
    catch(const std::exception &)
    {
      std::cerr << "Invalid playback rate: " << argv[2] << std::endl;
      printUsage(argv[0]);
      return 1;
    }
  }

  if(argc > 3)
  {
    looping = (std::string(argv[3]) == "loop");
  }

  // Create the playback instance with specified rate and looping preference
  VoyantPlayback player(playbackRate, looping);

  if(!player.isValid())
  {
    std::cerr << "Failed to create VoyantPlayback instance: " << player.getLastError() << std::endl;
    return 1;
  }

  // Open the file
  std::cout << "Opening file: " << filePath << std::endl;
  if(!player.openFile(filePath))
  {
    std::cerr << "Failed to open file: " << player.getLastError() << std::endl;
    return 1;
  }

  // Read and process frames - timing and loopback is handled automatically
  while(player.nextFrame())
  {
    // Get metadata about the frame
    size_t frameIndex = player.currentFrameIndex();
    uint64_t timestamp = player.currentFrameTimestamp();

    // Access latest frame as a const reference
    const VoyantFrameWrapper &frame = player.currentFrame();

    // Print frame metadata & frame debug string
    std::cout << "###############" << std::endl;
    std::cout << "Frame " << frameIndex << " (timestamp: " << std::fixed << std::setprecision(3)
              << timestamp / 1000000000.0 << "s)" << std::endl;
    std::cout << frame << std::endl;
  }

  // Check if we exited the loop due to an error
  if(!player.getLastError().empty())
  {
    std::cerr << "Error during playback: " << player.getLastError() << std::endl;
    return 1;
  }

  std::cout << "\nPlayback complete!" << std::endl;
  std::cout << "Processed " << player.getFramesProcessed() << " frames" << std::endl;

  return 0;
}
