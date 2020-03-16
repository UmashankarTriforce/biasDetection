#pragma once

#include <iostream>
#include <vector>
#include <CL/cl.hpp>

template <typename T>
class Graph {

private:
	std::vector<T> arr;

public:

	Graph(std::vector< std::vector<T> > host); //Init Graph
	void printGraph(); // Print Graph
};

template <typename T>::Graph<T>::Graph(std::vector< std::vector<T> > host) {

	//Initialize the Graph in the format of <number of nodes>,<cumulative number of edges>,<edges>

	arr.push_back(host.size());
	int count = 0;
	arr.push_back(count);
	for (auto i = 0; i < arr[0]; ++i) {
		count += host[i].size();
		arr.push_back(count);
	}
	for (auto i = 0; i < arr[0]; ++i) {
		arr.insert(arr.begin() + arr[0] + 2 + arr[i + 1], host[i].begin(), host[i].end());
	}
}

template <typename T> void::Graph<T>::printGraph() {

	// Print the Graph

	for (auto i = 0; i < arr.size(); ++i) {
		std::cout << arr[i] << std::endl;
	}
}