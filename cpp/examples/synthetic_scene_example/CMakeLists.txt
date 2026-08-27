cmake_minimum_required(VERSION 3.15)
project(synthetic_scene_example)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(synthetic_scene_example synthetic_scene_example.cpp)

# Link with the Voyant API
target_link_libraries(synthetic_scene_example PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(synthetic_scene_example
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
