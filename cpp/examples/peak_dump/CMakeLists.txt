cmake_minimum_required(VERSION 3.15)
project(peak_dump)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(peak_dump peak_dump.cpp)

# Link with the Voyant API
target_link_libraries(peak_dump PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(peak_dump
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
