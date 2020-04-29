#pragma once

#include <iostream>
#include <vector>
#include <fstream>
#include <CL/cl.hpp>
#include <string>
#include <memory>
#include <stdlib.h>

#define __CL_ENABLE_EXCEPTIONS
#if defined(__APPLE__) || defined(__MACOSX)
#include <OpenCL/cl.cpp>
#else
#include <CL/cl.hpp>
#endif

template <typename T>
class Graph {

private:

	//Member types
	std::vector<T> hostArr;
	std::vector<T> deviceArr;

	//OpenCL types
	std::vector<cl::Platform> all_platforms;
	std::vector<cl::Device> all_devices;
	cl::Device default_device;

	//Member functions
	void test();

public:

	//Member functions
	Graph(std::vector< std::vector<T> > host, int platformID = 0, int deviceID = 0); //initialize Graph
	void printGraph(); // print graph
	void OpenCLPrintGraph();

};

template <typename T> void::Graph<T>::test() {
	const int N_ELEMENTS = hostArr[0];
	const int graphSize = hostArr.size();
	unsigned int platform_id = 0, device_id = 0;
	
	std::unique_ptr<int[]> graph(new int[graphSize]); // Or you can use simple dynamic arrays like: int* A = new int[N_ELEMENTS];
	std::unique_ptr<int[]> component(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> sizes(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> MIS(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> C_nodes(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> score(new int[N_ELEMENTS]);
	

	for(int i = 0; i < graphSize; i++){
		graph[i] = hostArr[i];
	}

	for (int i = 0; i < N_ELEMENTS; ++i) {
		
		component[i] = 0;
		sizes[i] = 0;
		MIS[i] = 0;
		score[i] = 0;

	}

	// Create a context
	cl::Context context({ default_device });

	// Create a command queue
	cl::CommandQueue queue = cl::CommandQueue(context, default_device);   // Select the device.

	// Create the memory buffers
	// cl::Buffer bufferK = cl::Buffer(context, CL_MEM_READ_ONLY, sizeof(int));
	cl::Buffer bufferGraph = cl::Buffer(context, CL_MEM_READ_WRITE, graphSize * sizeof(int));
	cl::Buffer bufferComponent = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferSizes = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferMIS = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferScore = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	
	cl::Buffer bufferResult = cl::Buffer(context, CL_MEM_WRITE_ONLY, N_ELEMENTS * sizeof(int));

	// Copy the input data to the input buffers using the command queue.
	queue.enqueueWriteBuffer(bufferGraph, CL_FALSE, 0, graphSize * sizeof(int), graph.get());
	queue.enqueueWriteBuffer(bufferComponent, CL_FALSE, 0, N_ELEMENTS * sizeof(int), component.get());
	queue.enqueueWriteBuffer(bufferSizes, CL_FALSE, 0, N_ELEMENTS * sizeof(int), sizes.get());
	queue.enqueueWriteBuffer(bufferMIS, CL_FALSE, 0, N_ELEMENTS * sizeof(int), MIS.get());
	queue.enqueueWriteBuffer(bufferScore, CL_FALSE, 0, N_ELEMENTS * sizeof(int), score.get());

	// Read the program source 
	std::ifstream sourceFile("/home/thejas/Sem 6/HP/biasDetection/src/kernels/gpuCNDP.cl");
	std::string sourceCode(std::istreambuf_iterator<char>(sourceFile), (std::istreambuf_iterator<char>()));
	cl::Program::Sources source(1, std::make_pair(sourceCode.c_str(), sourceCode.length()));

	// Make program from the source code
	cl::Program program = cl::Program(context, source);

	// Build the program for the devices
	program.build({ default_device });

	// Make kernel
	cl::Kernel vecadd_kernel(program, "cndp");
	// the parameters are int k, int *graph, int* MIS, int *component, int *sizes, int *score
	// Set the kernel arguments
	vecadd_kernel.setArg(0, bufferGraph);
	vecadd_kernel.setArg(1, bufferMIS);
	vecadd_kernel.setArg(2, bufferComponent);
	vecadd_kernel.setArg(3, bufferSizes);
	vecadd_kernel.setArg(4, bufferScore);
	vecadd_kernel.setArg(5, bufferResult);

	// Execute the kernel
	cl::NDRange global(N_ELEMENTS);
	cl::NDRange local(1);
	queue.enqueueNDRangeKernel(vecadd_kernel, cl::NullRange, global, local);

	// Copy the output data back to the host
	queue.enqueueReadBuffer(bufferResult, CL_TRUE, 0, N_ELEMENTS * sizeof(int), C_nodes.get());

	// Verify the result
	bool result = true;
	for (int i = 0; i < N_ELEMENTS; i++)
		if (C_nodes[i] != hostArr[i]) {
			std::cout << C_nodes[i] << std::endl;
			result = false;
			break;
		}
			
	if (result)
		std::cout << "Success!\n";
	else
		std::cout << "Failed!\n";

	std::cout << "Done.\n";
}

template <typename T>::Graph<T>::Graph(std::vector< std::vector<T> > host, int platformID, int deviceID) {

	//Initialize and get all devices with OpenCL

	cl::Platform::get(&all_platforms);
	if (all_platforms.size() == 0) {
		std::cout << " No platforms found. Check OpenCL installation!" << std::endl;
		exit(1);
	}

	all_platforms[platformID].getDevices(CL_DEVICE_TYPE_ALL, &all_devices);
	if (all_devices.size() == 0) {
		std::cout << " No devices found. Check OpenCL installation!" << std::endl;
		exit(1);
	}

	std::cout << "Using platform: " << all_platforms[platformID].getInfo <CL_PLATFORM_NAME> () << std::endl;
	std::cout << "Using device: " << all_devices[deviceID].getInfo <CL_DEVICE_NAME> () << std::endl;

	default_device = all_devices[deviceID];

	//Initialize the Graph in the format of <number of nodes>,<cumulative number of edges>,<edges>

	hostArr.push_back(host.size());
	int count = 0;
	hostArr.push_back(count);
	for (auto i = 0; i < hostArr[0]; ++i) {
		count += host[i].size();
		hostArr.push_back(count);
	}
	for (auto i = 0; i < hostArr[0]; ++i) {
		hostArr.insert(hostArr.begin() + hostArr[0] + 2 + hostArr[i + 1], host[i].begin(), host[i].end());
	}

	test();

}

template <typename T> void::Graph<T>::printGraph() {

	// Print the Graph

	for (auto i = 0; i < hostArr.size(); ++i) {
		std::cout << hostArr[i] << std::endl;
	}
}

template <typename T> void::Graph<T>::OpenCLPrintGraph() {
}
