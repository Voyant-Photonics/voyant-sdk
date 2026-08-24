// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

#pragma once

// This file contains the command-line parsing functionality for the playback example

#include <iostream>
#include <string>

struct PlaybackOptions
{
    std::string filePath;
    double      playbackRate      = 1.0;
    bool        looping           = false;
    bool        keepInvalidPoints = false;
};

void printUsage(const char* programName)
{
    std::cerr << "Usage: " << programName << " <recording_file_path> [playback_rate] [loop] [keep_invalid]" << std::endl;
    std::cerr << "  recording_file_path: A .vynt recording. Convert a pre-v1.0.0 recording with" << std::endl;
    std::cerr << "                       voyant_recording_migrate first." << std::endl;
    std::cerr << "  playback_rate: Optional, controls playback speed (default: real-time)" << std::endl;
    std::cerr << "                 0 for as-fast-as-possible" << std::endl;
    std::cerr << "                 1.0 for real-time" << std::endl;
    std::cerr << "                 2.0 for double speed, etc." << std::endl;
    std::cerr << "  loop:          Optional, 'loop' to enable looping (default: '')" << std::endl;
    std::cerr << "  keep_invalid:  Optional, 'keep_invalid' to keep invalid points (default: dropped)" << std::endl;
}

PlaybackOptions parsePlaybackCommandLine(int argc, char* argv[])
{
    if (argc < 2)
    {
        printUsage(argv[0]);
        exit(1);
    }

    PlaybackOptions options;
    options.filePath = argv[1];

    if (argc > 2)
    {
        try
        {
            options.playbackRate = std::stod(argv[2]);
        }
        catch (const std::exception&)
        {
            std::cerr << "Invalid playback rate: " << argv[2] << std::endl;
            printUsage(argv[0]);
            exit(1);
        }
    }

    if (argc > 3)
    {
        options.looping = (std::string(argv[3]) == "loop");
    }

    if (argc > 4)
    {
        options.keepInvalidPoints = (std::string(argv[4]) == "keep_invalid");
    }

    return options;
}
