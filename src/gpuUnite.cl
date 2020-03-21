kernel int unite(int x, int total_score, int *graph, int *component, int *sizes, int *data, int *score){
	
	int thread_id = get_global_id(0);
	int united_component = any_neighbor_component(x, graph, component); //NOT DEFINED
	// clSyncThreads();
	reset_sizes_of_neighbor_component(x, graph, component, sizes, data, score); //NOT DEFINED
	int new_sizes = sum(data) + 1;
	int removed_scored = sum(scores);
	
	
}
