#pragma once

#include <iostream>
#include <vector>
#include <CL/cl.hpp>

template <typename T>
class Graph {
private:
	std::vector<T> arr;
	void printGraph(std::vector<T> arr);

public:

	Graph(std::vector< std::vector<T> > host);
};

template <typename T>::Graph<T>::Graph(std::vector< std::vector<T> > host) {
	arr.push_back(host.size());
	int count = 0;
	for (auto i = 0; i < arr[0]; ++i) {
		arr.push_back(count);
		count += host[i].size();
	}
	for (auto i = 0; i < arr[0]; ++i) {
		arr.insert(arr.begin() + arr[0] + 1 + arr[i + 1], host[i].begin(), host[i].end());
	}

	Graph<T>::printGraph(arr);
}

template <typename T> void::Graph<T>::printGraph(std::vector<T> arr) {
	for (auto i = 0; i < arr.size(); ++i) {
		std::cout << arr[i] << std::endl;
	}
}