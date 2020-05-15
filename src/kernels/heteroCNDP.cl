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