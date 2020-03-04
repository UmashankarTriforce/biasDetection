import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np





def CNDP_serial(k, G):
    GSize = G.size()
    NodeList = G.nodes()
    components = list()
    for i in range(GSize):
        components.append(0)

    max_component = GSize
    sizes = list()
    for i in range(max_component):
        sizes.append(0)

    MIS = nx.maximal_independent_set(G)

    component_id = 1
    forbidden_count = 0

    for i in range(GSize):
        if(i in NodeList):
            component[i] = component_id
            sizes[component_id] = 1
            component_id += 1
        else
            forbidden_count += 1

    if forbidden_count < k:
        X = random.sample(range(0, len(MIS)), k - forbidden_count)
        for x in range(len(X)):
            sizes[component[NodeList[x]]] = 0
            component[NodeList[x]] = 0

    while(forbidden_count > k):
        cand_node = 

if __name__ == "__main__":
    k = 5

    randomlist = random.sample(range(0, 4950), 3000)

    G = nx.complete_graph(100)
    j = 0
    for i in G.edges:
        if(j in randomlist):
            G.remove_edge(i[0], i[1])
        j += 1
    CNDP_serial(k, G)
    # pos = nx.spring_layout(G)

    # nx.draw_networkx_nodes(G, pos, node_size=50)
    # nx.draw_networkx_edges(G, pos, edgelist=G.edges)
    # plt.show()

