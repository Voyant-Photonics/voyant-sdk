cmake_minimum_required(VERSION 3.15)
project(voyant_sdk_examples)

# Find the Voyant API package
find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)

# Available SDK examples
add_subdirectory(voyant_client_basic)
add_subdirectory(voyant_playback_basic)
