from random import seed 
from random import random
from matplotlib import pyplot as plt
import math

def serial(V, E):
    return V*(V+E)

def parallel(V, T, max_degree):
    return (V*V/T*max_degree*max_degree) + V*math.log(T)


max_degree = 100
E = int(random())
T = 102400
serial_plot = []
node_plot = range(1, 10000000, 100)
parallel_plot = []
speedup_plot = []

for i in node_plot:
    serial_plot.append(serial(i, E))
    parallel_plot.append(parallel(i, T, max_degree))
    speedup_plot.append(serial(i, E) / parallel(i, T, max_degree))

plt.plot(node_plot, serial_plot, label='Serial Runtime')
plt.plot(node_plot, parallel_plot, label='Parallel Runtime')
plt.legend()
plt.xlabel('Nodes')
plt.ylabel('Time')
#plt.plot(node_plot, speedup_plot)
plt.show()
