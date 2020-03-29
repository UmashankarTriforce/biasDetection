add_library(graph_library INTERFACE)
target_include_directories(graph_library INTERFACE ../include)
target_link_libraries(graph_library INTERFACE OpenCL::OpenCL)

