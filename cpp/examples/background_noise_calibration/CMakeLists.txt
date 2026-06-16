cmake_minimum_required(VERSION 3.15)
project(background_noise_calibration)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(background_noise_calibration background_noise_calibration.cpp)

# Link with the Voyant API
target_link_libraries(background_noise_calibration PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(background_noise_calibration
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
