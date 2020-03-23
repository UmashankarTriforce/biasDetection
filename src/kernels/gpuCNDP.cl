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
	return result;
}


void nextCandidate(int *graph, int graphSize, int *data, int dataSize, int total_score, int *component, int *sizes, int *score){

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

int sum (int *data, int T){
  int threadID = get_global_id(0);
  // clSyncthread();
  int t = T;
  int h = t / 2;
  while (t > 1){
    if (threadID + h < t){
      data[threadID] = data[threadID] + data[threadID + h];
    }
    t = t / 2;
    h = h / 2;
    // clSyncthread();
    }
  return data[0];
}

int unite(int x, int total_score, int *graph, int *component, int *sizes, int *data, int *score){

  int thread_id = get_global_id(0);
  int united_component = any_neighbor_component(x, graph, component); //NOT DEFINED
  // clSyncThreads();
  reset_sizes_of_neighbor_component(x, graph, component, sizes, data, score); //NOT DEFINED
  int new_sizes = sum(data) + 1;
  int removed_scores = sum(scores);
  reassign_components(x, graph.max_node(), united_component, component, sizes); // NOT DEFINED
  // clSyncThreads();

  if (thread_id == 0){
    sizes[united_component] = new_sizes;
    component[x] = united_component;
  }

  total_score = total_score - removed_scores + (new_sizes * (new_sizes + 1) / 2);
  return total_score;

}


kernel int cndp(int k, int *graph, int *component, int *sizes, int *score){

  int block_id = get_work_id(0);
  // component[] <- block_id.component
  // sizes[] <- block_id.sizes
  int selected_count = count_total_score(); // NOT DEFINED
  int forbidden_count = graph.V() - selected_count; // NOT DEFINED
  int total_score = compute_total_score(); //NOT DEFINED
  if (forbidden_count < k){
    remove_maximal_independent_set(k - forbidden_count); //NOT DEFINED
  }
  while(graph.forbidden_nodes() > k){
    next_candidate(graph, total_score, component, sizes, data, score);
    // clSyncThreads();
    int next_node = min(data, score);
    total_score = unite(next_node, total_score, graph, component, sizes, data, score);
    //clSyncThreads();
    forbidden_count = forbidden_count + 1;
  }

  return result;

}
