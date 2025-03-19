// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#include "playback_options.hpp"
#include <chrono>
#include <iomanip>
#include <iostream>
#include <string>
#include <voyant_playback.hpp>

int main(int argc, char *argv[])
{
  // Parse command line arguments
  PlaybackOptions options = parsePlaybackCommandLine(argc, argv);

  // Create the playback instance with specified rate and looping preference
  VoyantPlayback player(options.playbackRate, options.looping);
  if(!player.isValid())
  {
    std::cerr << "Failed to create VoyantPlayback instance: " << player.getLastError() << std::endl;
    return 1;
  }

  // Open the file
  std::cout << "Opening file: " << options.filePath << std::endl;
  if(!player.openFile(options.filePath))
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

  // Print some details about the playback
  std::cout << "\nPlayback complete!" << std::endl;
  std::cout << "Processed " << player.getFramesProcessed() << " frames" << std::endl;

  return 0;
}
