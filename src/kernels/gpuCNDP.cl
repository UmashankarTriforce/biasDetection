
int any_neighbor_component(private int x, global int *graph, global int *component){
  int neighbour_start = graph[0] + 2 + graph[x+1];
  // as of now the first neighbour is returned, need to include pseudo random generator for the index.
  return graph[neighbour_start];
}


void reset_sizes_of_neighbor_component(private int x, global int *graph, global int *component, global int *sizes, global int *data, global int *score){
   int neighbour_start = graph[0] + 2 + graph[x+1];
   int neighbour_length = graph[x+2] - graph[x+1];
   for(int i = neighbour_start; x < graph[0] && i <= neighbour_start + neighbour_length; i++){
     int comp = component[graph[i]];
     //must check here
     sizes[comp] = 0;
   }
}

void reassign_components(private int x, private int max_node, private int united_component, global int *component, global int *sizes){

  int component_size = max_node;
  // printf("%d\n", united_component);
  for(int i = 0; i < component_size; i++){
      int node = i+1;
      int comp = component[node];
      if(sizes[comp] == 0){
        component[node] = united_component;
      }

  }
}

//serial MIS algo
int initializeMIS(global int *graph, global int *result){
  int num_vertices = graph[0];

  for(int i=0; i<num_vertices; ++i) {
      result[i] = 0;
  }
  for(int i=1; i<=num_vertices; ++i) {
    int start = num_vertices + 2 + graph[i];
    int nn = graph[i+1] - graph[i];
    int flag = 1;
    for(int j = start; flag && j < start + nn; ++j) {

      if(result[graph[j]]) {
        flag = 0;
        // i = 0;
        break;
      }
    }
    if(flag){
      result[i-1] = 1;
    }
  }
  // printf("%d    %d\n", get_global_id(0) - 1, result[get_global_id(0) - 1]);
  return 1;
}


int count_total_score(global int *score, private int n){
  int sum = 0;
  for(int i = 0; i < n; i++){
    sum += score[i];
  }
  return sum;
}


float score_with_node(private int x, private int total_score, global int *graph, global int* size, global int *component){
	int beg = graph[x];
	int end = graph[x + 1];

  float threshold = 1000000.0;
	if ((float)(end - beg) > threshold){
		return threshold;
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

int minNode(global int* data, global int* score, private int size){
  int min = INT_MAX;
  int res = data[0];
  for(int i = 0; i < size; i++){
    if(score[i] < min){
      res = data[i];
    }
  }
  return res;
}

// //thread_id, graph, total_score, component, sizes, data, score
void nextCandidate(const private int tid, global int *graph, private int total_score, global int *component, global int *sizes, global int *data, global int *score){

  int thread_id = tid;
  float min_score = 35000.0;
  int graphSize = graph[0];
  int candidate = 0;
  // find the number of threads!!
  for (int i = thread_id + 1; i <= graphSize; i++){
    int node_id = i;
    if (component[node_id] == 0){
      float score = score_with_node(node_id, total_score, graph, sizes, component);
      if (score < min_score){
        min_score = score;
        candidate = node_id;
      }
    }
  }
  data[thread_id] = candidate;
  score[thread_id] = min_score;
}

int sum (global int *data, private int T){
  int threadID = get_global_id(0);
  barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
  int t = T;
  int h = t / 2;
  while (t > 1){
    if (threadID + h < t){
      data[threadID] = data[threadID] + data[threadID + h];
    }
    t = t / 2;
    h = h / 2;
    barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
    }
  return data[0];
}


// // next_node, total_score, graph, component, sizes, data, scores
int unite(private int x, private int total_score, global int *graph, global int *component, global int *sizes, global int *data, global int *score){

  int thread_id = get_global_id(0);
  int united_component = any_neighbor_component(x, graph, component);

  barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
  reset_sizes_of_neighbor_component(x, graph, component, sizes, data, score);
  int new_sizes = sum(data, graph[0]) + 1;
  int removed_scores = sum_scores(score, graph[0]);
  int max_node = graph[0] - 1;
  reassign_components(x, max_node, united_component, component, sizes);
  barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);

  if (thread_id == 1){
    sizes[united_component] = new_sizes;
    component[x] = united_component;
  }

  total_score = total_score - removed_scores + (new_sizes * (new_sizes + 1) / 2);
  // printf("total %d\n", total_score);
  return total_score;

}


void remove_maximal_independent_set(global int *graph, global int *sizes, global int *component, global int *MIS, private int count){

  int n = graph[0];
  for(int i = 0; i < n; i++){
    if(MIS[i] && count){
      MIS[i] = 0;
      count--;
    }
  }
}

int selected_nodes(global int* MIS, private int size){
  int res = 0;
  for(int i = 0; i < size; i++){
    if(MIS[i]){
      res++;
    }
  }
  return res;
}

// int k, int *graph, int* MIS, int *component, int *sizes, int *score
kernel void cndp(global int* graph, global int *MIS, global int* component, global int* data, global int* sizes, global int* score, global int* result){
  int idx = get_group_id(0);
  int thread_id = get_global_id(0);
  int NUM = graph[0];

  // int data[7483];

  result[thread_id] = graph[thread_id];
  // // component[] <- block_id.component
  // // sizes[] <- block_id.sizes

  // barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
  int r = initializeMIS(graph, MIS);

  // barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);

  int k = 2778;
  int selected_count = selected_nodes(MIS, graph[0]);
  int forbidden_count = graph[0] - selected_count;
  int total_score = count_total_score(score, graph[0]);
  // printf("%d\n", forbidden_count);
  if (forbidden_count < k){
    remove_maximal_independent_set(graph, sizes, component, MIS, k - forbidden_count);
  }
  while(forbidden_count > k){
    nextCandidate(thread_id, graph, total_score, component, sizes, data, score);
    barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
    int next_node = minNode(data, score, graph[0]);
    //need to add the critical nodes after this.
    total_score = unite(next_node, total_score, graph, component, sizes, data, score);
    barrier(CLK_LOCAL_MEM_FENCE | CLK_GLOBAL_MEM_FENCE);
    forbidden_count = forbidden_count - 1;
  }
}
