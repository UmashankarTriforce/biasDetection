#include <boost/algorithm/string.hpp>
#include <fstream>
#include <iostream>
#include <graph.hpp>
#include <unordered_map>

using namespace std;

void test_on_dummy() {
	std::vector<std::vector <int> > test{
		{3, 1},
		{0, 2, 3},
		{1, 3},
		{2, 1, 0, 4},
		{3}
	};

	Graph<int> Test(test);

}

int main(){
	//testing on the dummy graph;
	// test_on_dummy();
    ifstream myfile("/home/thejas/Sem 6/HP/biasDetection/scripts/test.adjlist");
    string line;
    vector<vector<int>> adjlist;
    unordered_map<float, int> map;

    if(myfile.is_open()){
        vector<string> result;
		int k = 0;
        while(getline(myfile, line)){
            vector<int> temp;
            boost::split(result, line, boost::is_any_of(","));
            for(int i = 0; i < result.size(); i++){
				float key = stof(result[i]);
				if(map.find(key) == map.end()){
					map[key] = k;
					temp.push_back(k++);
				}
				else{
					temp.push_back(map[key]);
				}
            }
            adjlist.push_back(temp);
        }
    }
    else{
        cout << "not able to open the file please check the input path in testFile.cpp file" << endl;
    }

    Graph<int> Test(adjlist);
    return 0;
}