import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np
from operator import itemgetter

def any_neighbour_component(G, x, component, marked):
    neighbors = G.neighbors(x)
    for neighbor in neighbors:
        comp = component[neighbor]
        
        if not marked[comp]:
            return component[comp]
    return x


def unite(G, x, marked, united_comp, sizes, components):
    components[x] = united_comp
    sizes[united_comp] += 1
    neighbors = list(G.neighbors(x))
    neighborhoodSize = len(neighbors)
    nodeList = G.nodes()
    for i in range(neighborhoodSize):
        neighbor = neighbors[i]
        component = components[neighbor]
        if (np.logical_xor(component != united_comp, np.logical_xor(component != 0, marked[component] != 1))):
            marked[component] = 1
    
    for node in nodeList:
        comp = components[node]
        
        if(np.logical_xor(comp != united_comp, np.logical_xor(comp != 0, marked[comp] == 1))):
            components[node] = united_comp
            sizes[comp] -= 1
            sizes[united_comp] += 1

    for i in range(len(marked)):
        marked[i] = 0
    


def score_with_node(G, x, total_score, marked, sizes, component):
    new_size = 1
    neighbors = list(G.neighbors(x))
    neighborhoodSize = len(neighbors)
    
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
        comp_i = component[neighbors[i]]
        marked[comp_i] = 0

    return result

def next_candidate(G, component, sizes, marked):
    min_score = np.inf
    candidate = 0
    total_score = 0
    nodeList = G.nodes()
    # print(len(component))
    max_component = max(G.nodes())
    for c in range(max_component):
        total_score += sizes[c]*(sizes[c] - 1) / 2

    for node in nodeList:
        if(component[node] == 0):
            
            score = score_with_node(G, node, total_score, marked, sizes, component)
            print(score, min_score)
            if(score < min_score):
                
                min_score = score
                # print(node)
                candidate = node
    # print(candidate)
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
    k = 2
    
    randomlist = random.sample(range(0, 4950), 4800)

    G = nx.complete_graph(100)
    j = 0
    G1 = nx.Graph()
    G1.add_nodes_from(G)
    edgeList = G.edges
    for i in edgeList:
        if(j not in randomlist):
            G1.add_edge(i[0], i[1])
        j += 1
    # print(G.size(), G1.size(), len(G.nodes()))
    
    C_nodes = CNDP_serial(k, G1)
    # critical_nodes = list(set(C_nodes))
    # degree_all = []
    # useless = []
    # for i in G.nodes():
    #     if(i in critical_nodes):
    #         degree_all.append(G1.degree(i))
    #     else:
    #         useless.append(G1.degree(i))
    # print(useless, degree_all)
    


    # pos = nx.spring_layout(G1)

    # nx.draw_networkx_nodes(G1, pos, node_size=50)
    # nx.draw_networkx_edges(G1, pos, edgelist=G1.edges)
    # plt.show()

