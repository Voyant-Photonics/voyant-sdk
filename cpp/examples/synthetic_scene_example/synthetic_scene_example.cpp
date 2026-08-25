// Copyright (c) 2024-2025 Voyant Photonics, Inc.
//
// This example code is licensed under the MIT License.
// See the LICENSE file in the repository root for full license text.

// Record a synthetic scene as a .vynt log: build each frame from generated
// points with VoyantFrame::synthetic(), declare the scan configuration with
// withSdl(), and record the sequence — the output opens in the visualizer and
// replays like any sensor recording, identified by its "SIM-SW" device id.
//
// The scene is deliberately simple — a wall of points on an equally spaced
// azimuth/elevation grid whose range drifts over time. Swap generateWall() for
// your own generator and keep the rest of the loop as is.
//
// Usage: synthetic_scene_example [output.vynt] [n_frames]

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <logging_utils_ffi.hpp>
#include <optional>
#include <string>
#include <vector>
#include <voyant_data_recorder.hpp>
#include <voyant_frame.hpp>

namespace
{

// Scene geometry: an equally spaced angular grid, azimuth-fastest, with
// (azimuth_idx, elevation_idx) = (0, 0) at the top-left like a camera image.
constexpr size_t kElevations = 16;
constexpr size_t kAzimuths   = 128;
constexpr float  kHfovDeg    = 90.0f;
constexpr float  kVfovDeg    = 20.0f;
constexpr double kFps        = 10.0;
constexpr float  kPi         = 3.14159265f; // M_PI is POSIX-only

constexpr float degToRad(float deg)
{
    return deg * kPi / 180.0f;
}

// A wall of points; range drifts per frame so playback visibly moves.
std::vector<PointData> generateWall(uint32_t frameNumber)
{
    const float rangeM = 10.0f + 2.0f * std::sin(2.0f * kPi * frameNumber / 50.0f);
    const float azStep = degToRad(kHfovDeg) / (kAzimuths - 1);
    const float elStep = degToRad(kVfovDeg) / (kElevations - 1);

    std::vector<PointData> points;
    points.reserve(kElevations * kAzimuths);
    for (size_t el = 0; el < kElevations; ++el)
    {
        for (size_t az = 0; az < kAzimuths; ++az)
        {
            PointData point{};
            point.range_m = rangeM;
            // Azimuth sweeps left to right; elevation descends so index 0 is the top line.
            point.azimuth_rad   = -degToRad(kHfovDeg) / 2.0f + az * azStep;
            point.elevation_rad = degToRad(kVfovDeg) / 2.0f - el * elStep;
            point.snr           = 20.0f;
            point.azimuth_idx   = static_cast<uint16_t>(az);
            point.elevation_idx = static_cast<uint16_t>(el);
            point.drop_reason   = DROP_REASON_VALID;
            points.push_back(point);
        }
    }
    return points;
}

} // namespace

int main(int argc, char* argv[])
{
    voyant_log_init_c();
    const std::string outputPath = argc > 1 ? argv[1] : "synthetic_scene.vynt";
    // strtoll over stoul: one check covers empty/junk input, trailing characters, and
    // a stray "-1", which stoul would wrap into 4.29 billion frames.
    long long framesArg = 100;
    if (argc > 2)
    {
        char* end = nullptr;
        framesArg = std::strtoll(argv[2], &end, 10);
        if (end == argv[2] || *end != '\0' || framesArg < 0 || framesArg > UINT32_MAX)
        {
            std::cerr << "n_frames must be an integer in 0..4294967295" << std::endl;
            return 1;
        }
    }
    const uint32_t nFrames = static_cast<uint32_t>(framesArg);

    // The configuration the scene claims to have been generated under; replays as
    // applied sensor configuration (visible in the visualizer's state panels).
    SdlCommandParams sdl{};
    sdl.req_state          = static_cast<uint8_t>(SdlState::PointCloud);
    sdl.frame_rate_fps     = static_cast<float>(kFps);
    sdl.hfov_deg           = kHfovDeg;
    sdl.hfov_center_deg    = 0.0f;
    sdl.ramp_bandwidth_ghz = 8.0f;

    VoyantRecorderConfig recConfig(outputPath);
    recConfig.timestampFilename = false;
    VoyantRecorder recorder(recConfig);
    if (!recorder.isValid())
    {
        std::cerr << "Failed to create recorder for " << outputPath << ": " << recorder.getLastError() << std::endl;
        return 1;
    }

    const int64_t startSeconds  = 1700000000;
    const int64_t framePeriodNs = static_cast<int64_t>(1e9 / kFps);

    for (uint32_t i = 0; i < nFrames; ++i)
    {
        const int64_t totalNs = i * framePeriodNs;

        VoyantFrame::SyntheticFrameDesc desc;
        desc.source               = ProductId::SoftwareSimulator;
        desc.timestampSeconds     = startSeconds + totalNs / 1000000000;
        desc.timestampNanoseconds = static_cast<int32_t>(totalNs % 1000000000);
        desc.frameIndex           = i;

        std::optional<VoyantFrame> frame = VoyantFrame::synthetic(generateWall(i), desc);
        if (!frame)
        {
            std::cerr << "Failed to build synthetic frame " << i << std::endl;
            return 1;
        }
        std::optional<VoyantFrame> configured = frame->withSdl(sdl);
        if (!configured)
        {
            std::cerr << "SDL configuration rejected" << std::endl;
            return 1;
        }
        // No limits are configured, so Split/Finished cannot occur — anything but Ok failed.
        if (recorder.recordFrame(*configured) != RecordResult::Ok)
        {
            std::cerr << "Failed to record frame " << i << std::endl;
            return 1;
        }
    }

    if (!recorder.finalize())
    {
        std::cerr << "Failed to finalize recording" << std::endl;
        return 1;
    }

    std::cout << "Recorded " << nFrames << " synthetic frames to " << outputPath << std::endl;
    std::cout << "View it by running: voyant_visualizer --input " << outputPath << std::endl;
    return 0;
}
