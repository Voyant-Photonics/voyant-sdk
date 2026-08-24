// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

// Edit a Voyant recording and save it back: read each frame, filter or modify its
// points, rebuild the frame with withPoints(), and record the result to a new
// .vynt file.
//
// withPoints() returns a new frame that keeps everything else from the frame it
// came from — state snapshots, timestamps, frame index, device identity — so the
// output recording plays back like the input with only its points changed. The
// input file is read-only throughout; the edits land in a new file.
//
// The same flow works on live frames from a CarbonClient: filter or annotate each
// frame as it arrives, then record it.

#include <iostream>
#include <logging_utils_ffi.hpp>
#include <string>
#include <vector>
#include <voyant_data_recorder.hpp>
#include <voyant_playback.hpp>

void printUsage(const char* programName)
{
    std::cerr << "Usage: " << programName << " <input.vynt> <output.vynt> [max_range_m]" << std::endl;
    std::cerr << "  input.vynt:   Source recording. Convert a pre-v1.0.0 recording with" << std::endl;
    std::cerr << "                voyant_recording_migrate first." << std::endl;
    std::cerr << "  output.vynt:  Path for the edited recording" << std::endl;
    std::cerr << "  max_range_m:  Optional, drop points farther than this (default: 50)" << std::endl;
}

int main(int argc, char* argv[])
{
    voyant_log_init_c();

    if (argc < 3)
    {
        printUsage(argv[0]);
        return 1;
    }

    const std::string inputPath  = argv[1];
    const std::string outputPath = argv[2];
    float             maxRangeM  = 50.0f;

    if (argc > 3)
    {
        try
        {
            maxRangeM = std::stof(argv[3]);
        }
        catch (const std::exception&)
        {
            std::cerr << "Invalid max range: " << argv[3] << std::endl;
            printUsage(argv[0]);
            return 1;
        }
    }

    // Rate 0 replays as fast as possible; invalid returns are dropped as the frames
    // are read, so the output holds only valid points. Pass keep_invalid_points=true
    // to carry them through.
    VoyantPlayback player(0.0, false, false);
    if (!player.isValid())
    {
        std::cerr << "Failed to create VoyantPlayback: " << player.getLastError() << std::endl;
        return 1;
    }
    if (!player.openFile(inputPath))
    {
        std::cerr << player.getLastError() << std::endl;
        return 1;
    }

    VoyantRecorderConfig config(outputPath);
    config.timestampFilename = false;
    VoyantRecorder recorder(config);
    if (!recorder.isValid())
    {
        std::cerr << "Failed to create VoyantRecorder for " << outputPath << std::endl;
        return 1;
    }

    while (player.nextFrame())
    {
        const VoyantFrame& frame = player.currentFrame();

        // Any per-point edit works here. This one keeps near points and stamps the
        // user-owned bytes to mark the points this program touched.
        std::vector<PointData> kept;
        kept.reserve(frame.nPoints());
        for (const PointData& point : frame.points())
        {
            if (point.range_m <= maxRangeM)
            {
                kept.push_back(point);
                kept.back().user_data[0] = 1;
            }
        }

        VoyantFrame  edited = frame.withPoints(std::move(kept));
        RecordResult result = recorder.recordFrame(edited);
        if (result == RecordResult::Error)
        {
            std::cerr << "Failed to record frame " << edited.frameIndex() << std::endl;
            return 1;
        }

        std::cout << "frame " << edited.frameIndex() << ": kept " << edited.nPoints() << "/" << frame.nPoints()
                  << " points" << std::endl;

        // Finished is not an error: a configured limit was reached and the recorder
        // has already finalized itself.
        if (result == RecordResult::Finished)
        {
            break;
        }
    }

    if (!player.getLastError().empty())
    {
        std::cerr << "Error during playback: " << player.getLastError() << std::endl;
        return 1;
    }

    if (!recorder.finalize())
    {
        std::cerr << "Failed to finalize " << outputPath << std::endl;
        return 1;
    }

    std::cout << "Wrote " << outputPath << std::endl;
    return 0;
}
