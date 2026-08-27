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

    // The rate is optional, so argument 2 is a rate only when it is not a flag token --
    // otherwise 'file.vynt keep_invalid' would try to parse the flag as a number.
    int firstFlag = 2;
    if (argc > 2 && std::string(argv[2]) != "loop" && std::string(argv[2]) != "keep_invalid")
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
        firstFlag = 3;
    }

    // Either order, and an unrecognized token is rejected rather than ignored -- read
    // positionally, 'keep_invalid' alone was silently dropped without a 'loop' before it.
    for (int i = firstFlag; i < argc; ++i)
    {
        const std::string flag = argv[i];
        if (flag == "loop")
        {
            options.looping = true;
        }
        else if (flag == "keep_invalid")
        {
            options.keepInvalidPoints = true;
        }
        else
        {
            std::cerr << "Unknown option: " << flag << std::endl;
            printUsage(argv[0]);
            exit(1);
        }
    }

    return options;
}
