cmake_minimum_required(VERSION 3.15)

project(CNDP)

find_package(OpenCL REQUIRED)
add_executable(graph src/testFile.cpp)
target_link_libraries(graph OpenCL::OpenCL)
