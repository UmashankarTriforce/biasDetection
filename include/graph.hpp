#pragma once

#include <iostream>
#include <vector>
#include <CL/cl.hpp>

template <typename T>
class Graph {

private:

	//Member types
	std::vector<T> hostArr;
	std::vector<T> deviceArr;

	//OpenCL types
	std::vector<cl::Platform> all_platforms;
	std::vector<cl::Device> all_devices;
	cl::Platform default_platform;
	cl::Device default_device;

	//Member functions
	void initOpenCL(); // initialize opencl context
	void sendDataToDevice(); //send the data from host to device

public:

	//Member functions
	Graph(std::vector< std::vector<T> > host); //initialize Graph
	void printGraph(); // Print Graph

};

template <typename T>::Graph<T>::Graph(std::vector< std::vector<T> > host) {

	//Initialize the Graph in the format of <number of nodes>,<cumulative number of edges>,<edges>

	initOpenCL();

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

template <typename T> void::Graph<T>::printGraph() {

	// Print the Graph

	for (auto i = 0; i < hostArr.size(); ++i) {
		std::cout << hostArr[i] << std::endl;
	}
}

template <typename T> void::Graph<T>::initOpenCL() {

	//Initialize and get all devices with OpenCL 

	cl::Platform::get(&all_platforms);
	if (all_platforms.size() == 0) {
		std::cout << " No platforms found. Check OpenCL installation!\n";
		exit(1);
	}

	default_platform = all_platforms[0];
	std::cout << "Using platform: " << default_platform.getInfo<CL_PLATFORM_NAME>() << "\n";

	//get default device of the default platform
	default_platform.getDevices(CL_DEVICE_TYPE_ALL, &all_devices);
	if (all_devices.size() == 0) {
		std::cout << " No devices found. Check OpenCL installation!\n";
		exit(1);
	}
	default_device = all_devices[0];
	std::cout << "Using device: " << default_device.getInfo<CL_DEVICE_NAME>() << "\n";
}