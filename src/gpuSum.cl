kernel int sum (int *data, int T){
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
