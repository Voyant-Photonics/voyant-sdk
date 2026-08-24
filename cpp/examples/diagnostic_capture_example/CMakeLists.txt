cmake_minimum_required(VERSION 3.15)
project(diagnostic_capture_example)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(diagnostic_capture_example diagnostic_capture_example.cpp)

# Link with the Voyant API
target_link_libraries(diagnostic_capture_example PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(diagnostic_capture_example
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
