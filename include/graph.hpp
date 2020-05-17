#pragma once

#include <iostream>
#include <vector>
#include <fstream>
#include <CL/cl.hpp>
#include <string>
#include <memory>
#include <stdlib.h>
#include <utility>
#include <time.h>

#define __CL_ENABLE_EXCEPTIONS
#include <CL/cl.hpp>

template <typename T>
class Graph {

private:

	//Member types
	std::vector<T> hostArr;
	std::vector<T> deviceArr;

	//OpenCL types
	std::vector<cl::Platform> all_platforms;
	std::vector<std::vector<cl::Device>> all_devices_gpu;
    std::vector<std::vector<cl::Device>> all_devices_cpu;
	cl::Device default_cpu_device;
	cl::Device default_gpu_device;


	//Member functions


public:

	//Member functions
	Graph(std::vector< std::vector<T> > host); //initialize Graph
	void CNDPHetero();
	void CNDPParallel();

};

template <typename T>::Graph<T>::Graph(std::vector< std::vector<T> > host) {

	//Initialize and get all devices with OpenCL


	cl::Platform::get(&all_platforms);
	if (all_platforms.size() == 0) {
		std::cout << " No platforms found. Check OpenCL installation!" << std::endl;
		exit(1);
	}

    for (auto devices : all_platforms) {
        std::vector<cl::Device> cpu, gpu;
        devices.getDevices(CL_DEVICE_TYPE_CPU, &cpu);
        devices.getDevices(CL_DEVICE_TYPE_GPU, &gpu);
		if (cpu.size())
			all_devices_cpu.push_back(cpu);
		if(gpu.size())
			all_devices_gpu.push_back(gpu);
    }

    for (auto device_cpu : all_devices_cpu) {
        for(auto cpu: device_cpu)
            std::cout << "Detected CPU " << cpu.getInfo <CL_DEVICE_NAME>() << std::endl;
    }

    for (auto device_gpu : all_devices_gpu) {
        for (auto gpu: device_gpu)
            std::cout << "Detected GPU " << gpu.getInfo <CL_DEVICE_NAME>() << std::endl;
    }

	std::cout << std::endl;

	default_cpu_device = all_devices_cpu[0][0];
	default_gpu_device = all_devices_gpu[0][0];

	std::cout << "Using CPU " << default_cpu_device.getInfo <CL_DEVICE_NAME>() << std::endl;
	std::cout << "Using GPU " << default_gpu_device.getInfo <CL_DEVICE_NAME>() << std::endl;

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
}

template <typename T> void::Graph<T>::CNDPHetero() {

	const int graphSize = hostArr[0];

	std::unique_ptr<int []> graph(new int[graphSize]);
	std::unique_ptr<int []> components(new int[graphSize]);
	std::unique_ptr<int []> sizes(new int[graphSize]);
	std::unique_ptr<int []> MISResult(new int[graphSize]);
	std::unique_ptr<int	[]> data(new int[graphSize]);
	std::unique_ptr<int	[]> score(new int[graphSize]);
	std::unique_ptr<int	[]> tempArr(new int[2]);

	for (int i = 0; i < graphSize; ++i) {
		components[i] = 0;
		graph[i] = hostArr[i];
		data[i] = 0;
		score[i] = 0;
	}

	int maxComponent = graphSize;
	for (int i = 0; i < maxComponent; ++i)
		sizes[i] = 0;

	cl::Context CPUContext({ default_cpu_device });
	cl::Context GPUContext({ default_gpu_device });
	cl::CommandQueue CPUQueue(CPUContext, default_cpu_device);
	cl::CommandQueue GPUQueue(GPUContext, default_gpu_device);

	auto bufferGraph = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, graphSize * sizeof(int));
	auto bufferData = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, graphSize * sizeof(int));
	auto bufferResult = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, graphSize * sizeof(int));
	auto bufferScore = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, graphSize * sizeof(int));

	CPUQueue.enqueueWriteBuffer(bufferGraph, CL_FALSE | CL_MEM_USE_HOST_PTR, 0, graphSize * sizeof(int), graph.get());

	std::ifstream sourceFile("D:/Projects/biasDetection/src/kernels/heteroCNDP.cl");
	std::string sourceCode(std::istreambuf_iterator<char>(sourceFile), (std::istreambuf_iterator<char>()));
	cl::Program::Sources source(1, std::make_pair(sourceCode.c_str(), sourceCode.length()));

	auto CPUProgram = cl::Program(CPUContext, source);
	auto GPUProgram = cl::Program(GPUContext, source);
	CPUProgram.build({ default_cpu_device });
	GPUProgram.build({ default_gpu_device });

	cl::Kernel MISKernel(CPUProgram, "MISCPU");
	MISKernel.setArg(0, bufferGraph);
	MISKernel.setArg(1, bufferResult);

	cl::NDRange global(1);
	cl::NDRange local(graphSize);

	CPUQueue.enqueueNDRangeKernel(MISKernel, cl::NullRange, global, local);

	tempArr[0] = 1; //component_id
	tempArr[1] = 0; //forbidden_count

	auto bufferTemp = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, 2 * sizeof(int));
	auto bufferSize = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, maxComponent * sizeof(int));
	auto bufferComponent = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, graphSize * sizeof(int));
	CPUQueue.enqueueWriteBuffer(bufferTemp, CL_FALSE, 0, 2 * sizeof(int), tempArr.get());
	CPUQueue.enqueueWriteBuffer(bufferSize, CL_FALSE, 0, maxComponent * sizeof(int), sizes.get());
	CPUQueue.enqueueWriteBuffer(bufferComponent, CL_FALSE, 0, graphSize * sizeof(int), components.get());
	CPUQueue.enqueueWriteBuffer(bufferData, CL_FALSE, 0, graphSize * sizeof(int), data.get());
	CPUQueue.enqueueWriteBuffer(bufferScore, CL_FALSE, 0, graphSize * sizeof(int), score.get());

	cl::Kernel compKernel(CPUProgram, "CompCPU");
	compKernel.setArg(0, bufferComponent);
	compKernel.setArg(1, bufferSize);
	compKernel.setArg(2, bufferResult);
	compKernel.setArg(3, bufferTemp);

	CPUQueue.enqueueNDRangeKernel(compKernel, cl::NullRange, global, local);
	CPUQueue.enqueueReadBuffer(bufferTemp, CL_TRUE, 0, 2 * sizeof(int), tempArr.get());

	int k = 2774;
	if (tempArr[1] < k) {
		const int chosenNodeCount = k - tempArr[1];
		std::unique_ptr<int[]> chosenNodes(new int[chosenNodeCount]);
		srand(time(NULL));
		for (int i = 0; i < chosenNodeCount; ++i) {
			chosenNodes[i] = rand() % graphSize;
		}
		auto bufferChosenNodes = cl::Buffer(CPUContext, CL_MEM_READ_WRITE | CL_MEM_USE_HOST_PTR, chosenNodeCount * sizeof(int));
		CPUQueue.enqueueWriteBuffer(bufferChosenNodes, CL_FALSE, 0, chosenNodeCount * sizeof(int), chosenNodes.get());
		cl::Kernel trivialCPUKernel(CPUProgram, "trivialCPU");
		trivialCPUKernel.setArg(0, bufferChosenNodes);
		trivialCPUKernel.setArg(1, bufferSize);
		trivialCPUKernel.setArg(2, bufferComponent);
		cl::NDRange localTrivial(chosenNodeCount);
		CPUQueue.enqueueNDRangeKernel(trivialCPUKernel, cl::NullRange, global, localTrivial);
	}

	cl::Kernel nextCandidate(CPUProgram, "nextCandidate");
	nextCandidate.setArg(0, bufferGraph);
	nextCandidate.setArg(1, bufferComponent);
	nextCandidate.setArg(2, bufferSize);
	nextCandidate.setArg(3, bufferData);
	nextCandidate.setArg(4, bufferScore);

	cl::Kernel unite(GPUProgram, "unite");
	unite.setArg(0, bufferGraph);
	unite.setArg(1, bufferComponent);
	unite.setArg(2, bufferSize);
	unite.setArg(3, bufferData);
	unite.setArg(4, bufferScore);

	while (temp[1] > k) {
		CPUQueue.enqueueNDRangeKernel(nextCandidate, cl::NullRange, global, local);
		GPUQueue.enqueueNDRangeKernel(unite, cl::NullRange, global, local);
	}
}

template <typename T> void::Graph<T>::CNDPParallel() {
	const int N_ELEMENTS = hostArr[0];
	const int graphSize = hostArr.size();
	unsigned int platform_id = 0, device_id = 0;

	std::unique_ptr<int[]> graph(new int[graphSize]); // Or you can use simple dynamic arrays like: int* A = new int[N_ELEMENTS];
	std::unique_ptr<int[]> component(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> sizes(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> data(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> MIS(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> C_nodes(new int[N_ELEMENTS]);
	std::unique_ptr<int[]> score(new int[N_ELEMENTS]);

	for (int i = 0; i < graphSize; i++) {
		graph[i] = hostArr[i];
	}

	for (int i = 0; i < N_ELEMENTS; ++i) {

		component[i] = 0;
		sizes[i] = 0;
		MIS[i] = 0;
		score[i] = 0;
		data[i] = 0;

	}

	// Create a context
	cl::Context context({ default_gpu_device });

	// Create a command queue
	cl::CommandQueue queue = cl::CommandQueue(context, default_gpu_device);   // Select the device.

	// Create the memory buffers
	// cl::Buffer bufferK = cl::Buffer(context, CL_MEM_READ_ONLY, sizeof(int));
	cl::Buffer bufferGraph = cl::Buffer(context, CL_MEM_READ_WRITE, graphSize * sizeof(int));
	cl::Buffer bufferComponent = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferData = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferSizes = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferMIS = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferScore = cl::Buffer(context, CL_MEM_READ_WRITE, N_ELEMENTS * sizeof(int));
	cl::Buffer bufferResult = cl::Buffer(context, CL_MEM_WRITE_ONLY, N_ELEMENTS * sizeof(int));

	// Copy the input data to the input buffers using the command queue.
	queue.enqueueWriteBuffer(bufferGraph, CL_FALSE, 0, graphSize * sizeof(int), graph.get());
	queue.enqueueWriteBuffer(bufferComponent, CL_FALSE, 0, N_ELEMENTS * sizeof(int), component.get());
	queue.enqueueWriteBuffer(bufferData, CL_FALSE, 0, N_ELEMENTS * sizeof(int), data.get());
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
	vecadd_kernel.setArg(3, bufferData);
	vecadd_kernel.setArg(4, bufferSizes);
	vecadd_kernel.setArg(5, bufferScore);
	vecadd_kernel.setArg(6, bufferResult);

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



