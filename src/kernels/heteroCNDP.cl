kernel void MISCPU(global int* graph, global int* result) {

    const int i = get_global_id(0);
    result[i] = 0;
    int start = graph[0] + 2 + graph[i + 1];
    int nn = graph[i + 2] - graph[i + 1];
    int flag = 1;
    for (int j = start; flag && j < start + nn; ++j) {
        if (result[graph[j]]) {
            flag = 0;
            break;
        }
    }
    if (flag)
        result[i] = 1;
}

kernel void CompCPU(global int* component, global int* sizes, global int* MIS, global int* temp) {

    const int i = get_global_id(0);
    if (MIS[i]){
        component[i] = temp[0];
        sizes[temp[0]] = 1;
        ++temp[0];
    }
    else{
        ++temp[1];
    }
}

kernel void trivialCPU(global int* nodes, global int* sizes, global int* components){

    const int i = get_global_id(0);
    const int nodeValue = nodes[i];
    sizes[components[nodeValue]] = 0;
    components[nodeValue] = 0;
}

float score_with_node(private int x, private int total_score, global int* graph, global int* size, global int* component) {
    int beg = graph[x];
    int end = graph[x + 1];

    float threshold = 1000000.0;
    if ((float)(end - beg) > threshold) {
        return threshold;
    }
    int new_size = 1;
    for (int i = beg; i < end; ++i) {
        int c = component[graph[i]];

        if (c != 0) {
            bool was = false;
            for (int j = beg; j < i; ++j) {
                if (component[graph[j]] == c) {
                    was = true;
                    break;
                }
            }
            if (was == 0) {
                int s = size[c];
                total_score = total_score - (s * (s - 1) / 2);
                new_size = new_size + s;
            }
        }
    }

    float result = total_score + (new_size * (new_size - 1) / 2);
    return result;
}

kernel void nextCandidate(global int* graph, private int total_score, global int* component, global int* sizes, global int* data, global int* score) {

    int thread_id = get_global_id(0);
    float min_score = 35000.0;
    int graphSize = graph[0];
    int candidate = 0;
    // find the number of threads!!
    for (int i = thread_id + 1; i <= graphSize; i++) {
        int node_id = i;
        if (component[node_id] == 0) {
            float score = score_with_node(node_id, total_score, graph, sizes, component);
            if (score < min_score) {
                min_score = score;
                candidate = node_id;
            }
        }
    }
    data[thread_id] = candidate;
    score[thread_id] = min_score;
}

int any_neighbor_component(private int x, global int* graph, global int* component) {
    int neighbour_start = graph[0] + 2 + graph[x + 1];
    // as of now the first neighbour is returned, need to include pseudo random generator for the index.
    return graph[neighbour_start];
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

kernel void unite(private int x, private int total_score, global int *graph, global int *component, global int *sizes, global int *data, global int *score){

  int thread_id = get_global_id(0);
  int united_component = any_neighbor_component(x, graph, component);
  int new_sizes = sum(data, graph[0]) + 1;
  int removed_scores = sum_scores(score, graph[0]);
  int max_node = graph[0] - 1;

  if (thread_id == 1){
    sizes[united_component] = new_sizes;
    component[x] = united_component;
  }

  total_score = total_score - removed_scores + (new_sizes * (new_sizes + 1) / 2);

}