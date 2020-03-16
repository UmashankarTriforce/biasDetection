cmake_minimum_required(VERSION 3.15)

project(
	BiasDetection
	VERSION 0.1
	DESCRIPTION "Political Bias Detection on Twitter"
	LANGUAGES CXX
)

if(CMAKE_PROJECT_NAME STREQUAL PROJECT_NAME)
    
	set(CMAKE_CXX_EXTENSIONS OFF)
	set_property(GLOBAL PROPERTY USE_FOLDERS ON)

endif()

find_package(OpenCL REQUIRED)
add_subdirectory(src)
add_subdirectory(apps)