cmake_minimum_required(VERSION 3.15)
project(voyant_client_basic)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(voyant_client_basic voyant_client_basic.cpp)

# Link with the Voyant API
target_link_libraries(voyant_client_basic PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(voyant_client_basic
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
