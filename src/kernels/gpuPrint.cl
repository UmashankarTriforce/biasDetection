__kernel void gpuGraph(__global int* graphHost, __global int *graphDev) {
	const int idx = get_global_id(0);
	graphDev[idx] = graphHost[idx] * graphHost[idx];
}