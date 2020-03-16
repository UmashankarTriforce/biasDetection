#pragma once

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