add_library(graph_library INTERFACE)
target_include_directories(graph_library INTERFACE ../include)
target_link_libraries(graph_library INTERFACE OpenCL::OpenCL)

configure_file(kernels/gpuCNDP.cl ${RUNTIME_OUTPUT_DIRECTORY}/kernels/gpuCNDP.cl COPYONLY)
configure_file(kernels/gpuPrint.cl ${RUNTIME_OUTPUT_DIRECTORY}/kernels/gpuPrint.cl COPYONLY)
configure_file(kernels/vector_add_kernel.cl ${RUNTIME_OUTPUT_DIRECTORY}/kernels/vector_add_kernel.cl COPYONLY)