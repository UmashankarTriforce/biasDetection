#include <graph.hpp>

#include <vector>

int main() {
	std::vector<std::vector <int> > test{
		{3, 1},
		{0, 2, 3},
		{1, 3},
		{2, 1, 0, 4},
		{3}
	};

	Graph<int> Test(test);
	Test.printGraph();
	return 0;

}