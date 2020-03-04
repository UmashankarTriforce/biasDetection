import networkx as nx
import matplotlib.pyplot as plt
import random 
import numpy as np


randomlist = random.sample(range(0, 4950), 3000)

G = nx.complete_graph(100)
j = 0
for i in G.edges:
    if(j in randomlist):
        G.remove_edge(i[0], i[1])
    j += 1

pos = nx.spring_layout(G)

nx.draw_networkx_nodes(G, pos, node_size=50)
nx.draw_networkx_edges(G, pos, edgelist=G.edges)
plt.show()

