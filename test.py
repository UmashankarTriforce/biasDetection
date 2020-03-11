import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np


def score_with_node(G, x, total_score, sizes, component):
    new_size = 1
    neighbors = list(G.neighbors(x))
    neighborhoodSize = len(neighbors)
    marked = []
    for i in range(G.size()):
        marked[i] = 0
    for i in range(neighborhoodSize):
        neighbor = neighbors[i]
        comp = component[neighbor]
        if(comp != 0 and not(marked[comp])):
            marked[comp] = 1
            comp_score = sizes[comp] * (sizes[comp] - 1) / 2
            total_score = total_score - comp_score
            new_size = new_size + sizes[comp]
    
    result = new_size * (new_size - 1)/2 + total_score
    for i in range(1, neighborhoodSize):
        marked[component[neighbors[i]]] = 0

    return result

def next_candidate(G, component, sizes):
    min_score = -np.inf
    candidate = -1
    total_score = 0
    max_component = max(G.nodes())
    for c in range(max_component):
        total_score += sizes[c]*(sizes[c] - 1) / 2

    for node in G.size():
        if(component[G.nodes[node]] == 0):
            score = score_with_node(node, total_score)
            if(score < min_score):
                min_score = score
                candidate = G.nodes[node]
    return candidate



def CNDP_serial(k, G):
    GSize = G.size()
    NodeList = G.nodes()
    component = list()
    for i in range(GSize):
        component.append(0)

    max_component = GSize
    sizes = list()
    marked = list()
    for i in range(max_component):
        sizes.append(0)
    for i in range(max_component):
        marked.append(0)

    MIS = nx.maximal_independent_set(G)

    component_id = 0
    forbidden_count = 0

    for i in range(GSize):
        if(i in NodeList):
            component[i] = component_id
            # print(len(sizes))
            sizes[component_id] = 1
            component_id += 1
        else:
            forbidden_count += 1

    if forbidden_count < k:
        X = random.sample(range(0, len(MIS)), k - forbidden_count)
        for x in range(len(X)):
            sizes[component[NodeList[x]]] = 0
            component[NodeList[x]] = 0

    while(forbidden_count > k):
        # print(component)
        
        cand_node = next_candidate(G, component, sizes, marked)
        united_comp = any_neighbour_component(G, cand_node, component, marked)
        unite(G, cand_node, marked, united_comp, sizes, component)
        forbidden_count -= 1
    # print(NodeList, MIS)
    return list(set(NodeList) - set(MIS))

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

