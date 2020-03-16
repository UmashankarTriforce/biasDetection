set(HEADER_LIST "${BiasDetection_SOURCE_DIR}/include/graph.hpp")
add_library(graph_library graph.cpp ${HEADER_LIST})
target_include_directories(graph_library PUBLIC ../include)
target_link_libraries(graph_library OpenCL::OpenCL)