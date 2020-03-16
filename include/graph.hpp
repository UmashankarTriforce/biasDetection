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
	cl::Device default_device;

	//Member functions
	void sendDataToDevice(); //send the data from host to device

public:

	//Member functions
	Graph(std::vector< std::vector<T> > host, int platformID = 0, int deviceID = 0); //initialize Graph
	void printGraph(); // print graph

};

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

	std::cout << "Using platform: " << all_platforms[platformID].getInfo<CL_PLATFORM_NAME>() << std::endl;
	std::cout << "Using device: " << all_devices[deviceID].getInfo<CL_DEVICE_NAME>() << std::endl;

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

}

template <typename T> void::Graph<T>::printGraph() {

	// Print the Graph

	for (auto i = 0; i < hostArr.size(); ++i) {
		std::cout << hostArr[i] << std::endl;
	}
}
