// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#include <carbon_client.hpp>
#include <carbon_config.hpp>
#include <chrono>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <optional>
#include <thread>
#include <voyant_data_recorder.hpp>

int main()
{
  // Initialize API internal logging
  voyant_log_init_c();

  std::cout << "Starting Voyant recording example..." << std::endl;

  // Set up signal handling for graceful shutdown (Ctrl+C)
  CarbonClient::setupSignalHandling();

  // Create a Carbon client
  // For local testing: use "127.0.0.1" as the interface IP
  // For a real sensor: use your network interface IP (e.g., "192.168.20.100")
  CarbonConfig config;
  config.setBindAddr("0.0.0.0:5678").setGroupAddr("224.0.0.0").setInterfaceAddr("192.168.1.100");

  // Optional: override defaults as needed
  // config.setRangeMax(50.0f);
  // config.setPfa(1e-4f);

  CarbonClient client(config);
  client.start();

  // --- Create recorder using the configuration struct ---
  // Required: Set the base path for the output file(s).
  VoyantRecorderConfig recConfig("test_recording/recording.vynt");

  // Example: Split files after 50 frames OR after reaching 20 MB, whichever comes first.
  recConfig.framesPerFile = 50;
  recConfig.sizePerFileMb = 20;

  // Example: Stop recording entirely after 200 total frames.
  recConfig.maxTotalFrames = 200;

  // Create the recorder with the specified configuration.
  VoyantRecorder recorder(recConfig);

  if(!recorder.isValid())
  {
    std::cerr << "Failed to create VoyantRecorder" << std::endl;
    return -1;
  }

  std::cout << "Listening for frames (press Ctrl+C to stop)..." << std::endl;

  // Main recording loop
  bool shouldContinue = true;
  while(client.isRunning() && !CarbonClient::isTerminated() && shouldContinue)
  {
    if(client.tryReceiveFrame())
    {
      // Get the latest frame
      const auto &frame = client.latestFrame();

      // Record the frame
      RecordResult result = recorder.recordFrame(frame);

      switch(result)
      {
        case RecordResult::Ok:
          // Normal successful recording - periodically log some stats
          {
            std::optional<size_t> maybe_total = recorder.getTotalFramesRecorded();
            if(maybe_total.has_value())
            {
              size_t total = maybe_total.value();
              if(total > 0 && total % 100 == 0)
              {
                std::cout << "Recorded " << total << " frames";

                std::optional<size_t> maybe_splits = recorder.getSplitCount();
                if(maybe_splits.has_value())
                {
                  size_t splits = maybe_splits.value();
                  if(splits > 0)
                  {
                    std::cout << " across " << splits << " files";
                  }
                }
                std::cout << std::endl;
              }
            }
          }
          break;

        case RecordResult::Split:
          // File was split - this is still successful recording
          {
            std::optional<size_t> maybe_total = recorder.getTotalFramesRecorded();
            std::optional<size_t> maybe_splits = recorder.getSplitCount();

            if(maybe_total.has_value() && maybe_splits.has_value())
            {
              size_t total = maybe_total.value();
              size_t splits = maybe_splits.value();
              std::cout << "File split occurred at frame " << total << " (now " << splits
                        << " files)" << std::endl;
            }
            else
            {
              std::cout << "File split occurred" << std::endl;
            }
          }
          break;

        case RecordResult::Finished:
          // Recording limits reached - stop gracefully
          std::cout << "Recording limits reached. Stopping..." << std::endl;
          shouldContinue = false;
          break;

        case RecordResult::Error:
          // An error occurred
          std::cerr << "Error recording frame" << std::endl;
          shouldContinue = false;
          break;

        case RecordResult::Unknown:
          // Unexpected result - treat as error
          std::cerr << "Unexpected recording result" << std::endl;
          shouldContinue = false;
          break;
      }
    }

    // Small delay to avoid busy-waiting
    if(shouldContinue)
    {
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
  }

  client.stop();

  // Finalize recording
  std::cout << "\nFinalizing recording..." << std::endl;
  if(!recorder.finalize())
  {
    std::cerr << "Failed to finalize VoyantRecorder" << std::endl;
    return 1;
  }

  std::cout << "Recording complete!" << std::endl;
  return 0;
}
