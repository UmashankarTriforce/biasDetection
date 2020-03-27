import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np
from operator import itemgetter
import cProfile
import pstats
import time
prof = cProfile.Profile()

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
            # print(score, min_score)
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
    # print(forbidden_count, len(MIS), len(set(MIS)))
    return list(set(NodeList) - set(MIS))
if __name__ == "__main__":
    k = 10
    


    time_plot = []
    for numNodes in range(100, 1000, 100):
        G = nx.complete_graph(numNodes)
        numEdges = len(G.edges)
        dropout = int(0.9 * numEdges)
        forbiddenEdges = random.sample(range(0, numEdges), dropout)
        j = 0
        G1 = nx.Graph()
        G1.add_nodes_from(G)
        edgeList = G.edges
        for i in edgeList:
            if(j not in forbiddenEdges):
                G1.add_edge(i[0], i[1])
            j += 1
        # print(G.size(), G1.size(), len(G.nodes()))
        start = time.process_time()
        C_nodes = CNDP_serial(k, G1)
        time_plot.append(time.process_time() - start)
        # print(C_nodes)
    print(time_plot)
 ################################################   
    # G1 = nx.read_adjlist("test.adjlist", nodetype = float, delimiter = ",")
    # n = len(G1.nodes)
    # mapping = dict(zip(G1, range(0, n)))
    # G1 = nx.relabel_nodes(G1,mapping)
    # # print(G1.nodes(), G1.edges())
    
    # # prof.enable()
    # C_nodes = CNDP_serial(k, G1)
    # # prof.disable()
    
    # # prof.dump_stats("result.prof")

    # # ps = pstats.Stats("result.prof")
    # # ps.sort_stats(pstats.SortKey.CUMULATIVE)
    # # ps.print_stats()

    # abs = mapping[float(111944435)]
    # isThere = abs in G1.nodes
##################################################
    # print(C_nodes, mapping, isThere)
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

