cmake_minimum_required(VERSION 3.15)
project(sdl_command)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(sdl_command sdl_command.cpp)

# Link with the Voyant API
target_link_libraries(sdl_command PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(sdl_command
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
