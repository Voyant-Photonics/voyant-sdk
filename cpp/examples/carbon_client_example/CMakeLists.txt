cmake_minimum_required(VERSION 3.15)
project(carbon_client_example)

# Find the voyant-api package if building this example directly
if(NOT TARGET voyant-api::voyant-api)
  find_package(voyant-api REQUIRED PATHS /usr/lib/cmake/voyant-api)
endif()

# Create executable
add_executable(carbon_client_example carbon_client_example.cpp)

# Link with the Voyant API
target_link_libraries(carbon_client_example PRIVATE voyant-api::voyant-api)

# Set output directory
set_target_properties(carbon_client_example
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
