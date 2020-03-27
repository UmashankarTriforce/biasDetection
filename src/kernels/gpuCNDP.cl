kernel void mis_neighbour_addition(int *graph, int *result, int nn) {
  const int idx = get_global_id(0);
  int start = num_vertices + 2 + graph[idx];
    int nn = graph[idx+1] - graph[idx];
    int flag = 1;
    for(int j = graph[idx]; j < graph[idx] + nn; ++j) {
      if(result[start + j]) {
        flag = 0;
        break;
      }
    }
    if(flag)
      result[idx] = 1;
  }
}


void any_neighbor_component(int x, int *graph, int *component){
  int neighbour_start = graph[0] + 2 + graph[x+1];
  // as of now the first neighbour is returned, need to include pseudo random generator for the index.
  return graph[neighbour_start]; 
}


void reset_sizes_of_neighbor_component(int x, int *graph, int *component, int *sizes, int *data, int *score){
   int neighbour_start = graph[0] + 2 + graph[x+1];
   int neighbour_length = graph[x+2] - graph[x+1]; 
   for(int i = neighbour_start; i < graph[x] + neighbour_length; i++){
     int comp = component[graph[i]];
     sizes[comp] = 0;
   }
}

void reassign_components(int x, int max_node, int united_component, int *component, int *sizes){
  
  int component_size = max_node;
  for(int i = 0; i < component_size; i++){
      int node = i+1;
      int comp = component[node];
      if(sizes[comp] == 0){
        component[node] = united_component;
      }    

    }
  }


void initializeMIS(int *graph, int *result){
  int num_vertices = graph[0];
  for(int i=0; i<num_vertices; ++i) {
      result[i] = 0
  }
  for(int i=1; i<=num_vertices; ++i) {
    int start = num_vertices + 2 + graph[i];
    int nn = graph[i+1] - graph[i];
    int flag = 1;
    for(int j = graph[i]; j < graph[i] + nn; ++j) {
      if(result[start + j]) {
        flag = 0;
        break;
      }
    }
    if(flag)
      result[i] = 1;
  }
}


int count_total_score(int *score, int n){
  int sum = 0;
  for(int i = 0; i < n; i++){
    sum += score[i];
  }
  return sum;
}


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
  int united_component = any_neighbor_component(x, graph, component);
  // clSyncThreads();
  reset_sizes_of_neighbor_component(x, graph, component, sizes, data, score);
  int new_sizes = sum(data) + 1;
  int removed_scores = sum(scores);
  int max_node = graph.max_node();
  reassign_components(x, max_node, united_component, component, sizes); 
  // clSyncThreads();

  if (thread_id == 0){
    sizes[united_component] = new_sizes;
    component[x] = united_component;
  }

  total_score = total_score - removed_scores + (new_sizes * (new_sizes + 1) / 2);
  return total_score;

}


void remove_maximal_independent_set(int *graph, int *sizes, int *component, int *MIS, int count){
  
  int n = graph[0];
  for(int i = 0; i < n; i++){
    if(MIS[i] && count){
      MIS[i] = 0;
      count--; 
    }
  }
}


kernel int cndp(int k, int *graph, int* MIS, int *component, int *sizes, int *score){
  
  int block_id = get_work_id(0);
  // component[] <- block_id.component
  // sizes[] <- block_id.sizes

  initializeMIS(graph, MIS);

  int selected_count = count_total_score(score); 
  int forbidden_count = graph[0] - selected_count; 
  int total_score = count_total_score(score); 
  if (forbidden_count < k){
    remove_maximal_independent_set(graph, sizes, component, MIS, k - forbidden_count); 
  }
  while(forbidden_count > k){
    next_candidate(graph, total_score, component, sizes, data, score);
    // clSyncThreads();
    int next_node = min(data, score);
    total_score = unite(next_node, total_score, graph, component, sizes, data, score);
    //clSyncThreads();
    forbidden_count = forbidden_count - 1;
  }

  return result;

}
