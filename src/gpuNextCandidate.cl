float score_with_node(int x, int total_score, int *graph, int *component, int *){
	int beg = graph[x];
	int end = graph[x + 1];
	if (end - beg > threshold){    // must bind threshold to a value
		return 99999999999.0
	}
	int new_size = 1;
	for (int i = beg; i < end; ++i){
		int c = component[graph[i]];
		if (c != 0){
			bool was = false;
			for (int j = beg; j < i; ++j){
				if (component[graph[j]] == c){
					was = true;
					break;
				}
			}
			if (was == 0){
				int s = size[c];
				total_score = total_score - (s * (s - 1) / 2);
				new_size = new_size + s;
			}
		}
	}
	float result = total_score + (new_size * (new_size - 1) / 2);
	return float;
}



kernel void nextCandidate(int *graph, int graphSize, int *data, int dataSize, int total_score, int *component, int *sizes, int *score){
	
	int thread_id = get_global_id(0);
	float min_score = 35000.0;
	for (int i = thread_id + 1; i <= graphSize; i += dataSize ){
		int node_id = graph[i];
		if (component[node_id] == 0){
			float sore = score_with_node(node_id, total_score, graph, sizes, components);
			if (score < min_score){
				min_score = score; 
				int candidate = node_id;
			}
		}
	}
	data[thread_id] = candidate;
	score[thread_id] = min_score;
}
