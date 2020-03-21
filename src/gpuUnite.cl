kernel int unite(int x, int total_score, int *graph, int *component, int *sizes, int *data, int *score){
	
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
