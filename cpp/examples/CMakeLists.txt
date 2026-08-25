cmake_minimum_required(VERSION 3.15)
project(voyant_sdk_examples)

# Find the Voyant API package
find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)

# Examples that need a live sensor
add_subdirectory(carbon_client_basic)
add_subdirectory(voyant_recorder_basic)
add_subdirectory(sdl_command)
add_subdirectory(background_noise_calibration)

# Examples that work on recording files
add_subdirectory(voyant_playback_basic)
add_subdirectory(edit_recording_example)
add_subdirectory(synthetic_scene_example)
