#!/usr/bin/env python
# coding: utf-8

# ### Import modules

# First of all, we'll import all useful modules to our notebook.

# In[1]:


#Import modules
get_ipython().run_line_magic('matplotlib', 'inline')

#handling data
import pandas as pd
import numpy as np
from scipy import stats
from operator import itemgetter

#import twitter credentials


#handling information
import re
import json

#handling plots
import matplotlib.pyplot as plt
import seaborn as sns

#for network creation
import networkx as nx


# ### Read json to DataFrame

# The information that we've collected is stored in the file 'tweets.txt'. Because this file has a JSON format, we'll take advantage of the `read_json` function of the pandas module. 

# In[2]:


pd.set_option('display.float_format', lambda x: '%.f' % x)


# In[3]:


# Read json into a pandas dataframe
tweets_df = pd.read_json("tweets_caa.txt", lines=True)


# According to [Twitter API website](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object), the Tweet object retrieved, provided in JSON format, has a long list of mixed `root-level` attributes, including basic information such as `id`, `created_at`, and `text`. Tweet objects are also the `parent` object to several child objects. Tweet child objects include `user`, `entities`, and extended_entities.

# In order to have a better idea of the information we are dealing with, let's take a look at the `DataFrame` columns.

# In[4]:


# Let's check the name of the columns
tweets_df.columns


# From the displayed columns, we can observe some of them that look interesting for our future analysis. If we look more in detail, certain columns, such as `retweeted_status`, `entities` provide us with information about interactions regarding user mentions and user retweets. So, we are going to create a new `DataFrame` where to store all this important information that will come in handy when we build our Network. 

# In[5]:


# Create a second dataframe to put important information
tweets_final = pd.DataFrame(columns = ["created_at", "id", "in_reply_to_screen_name", "in_reply_to_status_id", "in_reply_to_user_id",
                                      "retweeted_id", "retweeted_screen_name", "user_mentions_screen_name", "user_mentions_id", 
                                       "text", "user_id", "screen_name", "followers_count"])


# In[6]:


# Columns that are going to be the same
equal_columns = ["created_at", "id", "text"]
tweets_final[equal_columns] = tweets_df[equal_columns]


# Now, we need to obtain important information. There are three types of interactions between two Twitter users that we should gather: retweets, replies, and mentions.

# From the structure of the [JSON file](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/intro-to-tweet-json#tweetobject) retrieved by the Twitter API, we learn that we can obtain basic information about the user: 

# In[7]:


# Get the basic information about user 
def get_basics(tweets_final):
    tweets_final["screen_name"] = tweets_df["user"].apply(lambda x: x["screen_name"])
    tweets_final["user_id"] = tweets_df["user"].apply(lambda x: x["id"])
    tweets_final["followers_count"] = tweets_df["user"].apply(lambda x: x["followers_count"])
    return tweets_final


# The `entities` object is a dictionary that contains, among other information, the `user_mentions` object that represents other Twitter users (`screen_name` and `id`) mentioned in the text of the Tweet.  

# In[8]:


# Get the user mentions 
def get_usermentions(tweets_final):
    # Inside the tag 'entities' will find 'user mentions' and will get 'screen name' and 'id'
    tweets_final["user_mentions_screen_name"] = tweets_df["entities"].apply(lambda x: x["user_mentions"][0]["screen_name"] if x["user_mentions"] else np.nan)
    tweets_final["user_mentions_id"] = tweets_df["entities"].apply(lambda x: x["user_mentions"][0]["id_str"] if x["user_mentions"] else np.nan)
    return tweets_final


# The retweets always contain two Tweet objects: The original Tweet being Retweeted is provided in a `retweeted_status` object. Inside, the `user` object for the account (`screen_name` and `id`) taking the Retweet action and the time of the Retweet.  

# In[9]:


# Get retweets
def get_retweets(tweets_final):
    # Inside the tag 'retweeted_status' will find 'user' and will get 'screen name' and 'id'    
    tweets_final["retweeted_screen_name"] = tweets_df["retweeted_status"].apply(lambda x: x["user"]["screen_name"] if x is not np.nan else np.nan)
    tweets_final["retweeted_id"] = tweets_df["retweeted_status"].apply(lambda x: x["user"]["id_str"] if x is not np.nan else np.nan)
    return tweets_final


# From the Tweet object, we can get the information of the user and status to which the tweet replies to:

# In[10]:


# Get the information about replies
def get_in_reply(tweets_final):
    # Just copy the 'in_reply' columns to the new dataframe
    tweets_final["in_reply_to_screen_name"] = tweets_df["in_reply_to_screen_name"]
    tweets_final["in_reply_to_status_id"] = tweets_df["in_reply_to_status_id"]
    tweets_final["in_reply_to_user_id"]= tweets_df["in_reply_to_user_id"]
    return tweets_final


# Now, we define a function that calls all the functions to fill the DataFrame with the usefull variables.

# In[11]:


# Lastly fill the new dataframe with the important information
def fill_df(tweets_final):
    get_basics(tweets_final)
    get_usermentions(tweets_final)
    get_retweets(tweets_final)
    get_in_reply(tweets_final)
    return tweets_final


# It's time to get from the DataFrame all the interactions. For this aim, we'll define a function that will iterate over the DataFrame, obtain the user_id and screen_name of the user that the author of that specific tweet mention, reply or retweet. The function will return the user of the specific tweet together with a list of the users with whom the user interacted.

# In[12]:


# Get the interactions between the different users
def get_interactions(row):
    # From every row of the original dataframe
    # First we obtain the 'user_id' and 'screen_name'
    user = row["user_id"], row["screen_name"]
    # Be careful if there is no user id
    if user[0] is None:
        return (None, None), []
    
    # The interactions are going to be a set of tuples
    interactions = set()
    
    # Add all interactions 
    # First, we add the interactions corresponding to replies adding the id and screen_name
    interactions.add((row["in_reply_to_user_id"], row["in_reply_to_screen_name"]))
    # After that, we add the interactions with retweets
    interactions.add((row["retweeted_id"], row["retweeted_screen_name"]))
    # And later, the interactions with user mentions
    interactions.add((row["user_mentions_id"], row["user_mentions_screen_name"]))
    
    # Discard if user id is in interactions
    interactions.discard((row["user_id"], row["screen_name"]))
    # Discard all not existing values
    interactions.discard((None, None))
    # Return user and interactions
    return user, interactions


# Now, we fill the DataFrame and discard the None values.

# In[13]:


tweets_final = fill_df(tweets_final)


# Be aware of None values!

# In[14]:


tweets_final = tweets_final.where((pd.notnull(tweets_final)), None)


# In[15]:


tweets_final.head(5)


# Now, it's time to initialize the Graph. We can do this by calling the function .Graph() of NetworkX.

# There are two other important functions to create a Graph. The first one is add_node()and the second one, add_edge both with a very descriptive name. Let's pay attention to the syntax of add_edge:  
# 
# `Graph.add_edge(u_of_edge, v_of_edge, **attr)`  
# 
# where `u`, `v` are the nodes, and attr are keyword arguments that characterize the edge data such as weight, capacity, length, etc.
#   
# If we add an edge that already exists, the edge data will get updated. Also, if we are an edge between two nodes that are still not in the Graph, the nodes will be created in the process.
# We are going to populate the Graph by calling the function get_interactions that we defined earlier. With this information, we apply the function add_edge to every tuple consisting of the tweet's user_id and the user_id of the user mentioned, replied to or retweeted, creating the nodes and the edges connecting them. Also, the tweet id will be added as edge data.

# In[17]:


graph = nx.Graph()
for index, tweet in tweets_final.iterrows():
    user, interactions = get_interactions(tweet)
    user_id, user_name = user
    tweet_id = tweet["id"]
    #tweet_sent = tweet["sentiment"]
    for interaction in interactions:
        int_id, int_name = interaction
        graph.add_edge(user_id, int_id, tweet_id=tweet_id)
        

        graph.nodes[user_id]["name"] = user_name
        graph.nodes[int_id]["name"] = int_name       


# Now that we have the node and edge of the Graph created, let's see the number of nodes and edges present:

# In[18]:


print(f"There are {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges present in the Graph")


# The degree of a node u, denoted as deg(u), is the number of edges that occur to that node. In simpler words, the number of connections a particular node has. The maximum degree of a graph and the minimum degree of a graph are the maximum and minimum degree of its nodes, respectively.

# In[19]:


degrees = [val for (node, val) in graph.degree()]


# In[20]:


print(f"The maximum degree of the Graph is {np.max(degrees)}")   
print(f"The minimum degree of the Graph is {np.min(degrees)}")  


# In[21]:


print(f"The average degree of the nodes in the Graph is {np.mean(degrees):.1f}")  
print(f"The most frequent degree of the nodes found in the Graph is {stats.mode(degrees)[0][0]}") 


# An undirected graph is connected if, for every pair of nodes, there is a path between them. For that to happen, most of the nodes should have at least a degree of two, except for those denominated leaves which have a degree of 1. From the characteristics of the Graph, we can suspect that the graph is not connected. In order to confirm these, we can use `nx.is_connected`.

# In[22]:


if nx.is_connected(graph):
    print("The graph is connected")
else:
    print("The graph is not connected")


# Now, that we confirm that our Graph is not connected, we can check how many connected components it has:

# In[23]:


print(f"There are {nx.number_connected_components(graph)} connected components in the Graph")  


# In[24]:


largest_subgraph = max(nx.connected_component_subgraphs(graph), key=len)


# In[25]:


print(f"There are {largest_subgraph.number_of_nodes()} nodes and {largest_subgraph.number_of_edges()} edges present in the largest component of the Graph")


# In[26]:


if nx.is_connected(largest_subgraph):
    print("The graph is connected")
else:
    print("The graph is not connected")


# Clustering and transitivity measure the tendency for nodes to cluster together or for edges to form triangles. In our context, they are measures of the extent to which the users interacting with one particular user tend to interact with each other as well. The difference is that transitivity weights nodes with a large degree higher. 
# The clustering coefficient, a measure of the number of triangles in a graph, is calculated as the number of triangles connected to node i divided by the number of sets of two edges connected to node i (Triple nodes). While the transitivity coefficient is calculated as 3 multiply by the number of triangles in the network divided by the number of connected triples of nodes in the network. These two parameters are very important when analyzing social networks because it gives us an insight into how users tend to create tightly knot groups characterized by relatively high-dense ties.

# In[27]:


print(f"The average clustering coefficient is {nx.average_clustering(largest_subgraph)} in the largest subgraph")
print(f"The transitivity of the largest subgraph is {nx.transitivity(largest_subgraph)}")


# After that, we'll investigate some summary statistics, particularly related to distance, or how far away one node is from another random node. Diameter represents the maximum distance between any pair of nodes while the average distance tells us the average distance between any two nodes in the network.

# In[28]:


print(f"The diameter of our Graph is {nx.diameter(largest_subgraph)}")
print(f"The average distance between any two nodes is {nx.average_shortest_path_length(largest_subgraph):.2f}")


# Now, we are going to focus on **network centrality** which captures the importance of a node's position in the network considering: degree on the assumption that an important node will have many connections, closeness on the assumption that important nodes are close to other nodes, and finally, betweenness on the assumption that important nodes are well situated and connect other nodes. For this, we are going to use the following functions `degree_centrality`, `closenness_centrality` and `betwenness_centrality`, all which return a list of each node and its centrality score. We will particularly capture the node with the best score in each one.

# In[29]:


graph_centrality = nx.degree_centrality(largest_subgraph)


# In[30]:


max_de = max(graph_centrality.items(), key=itemgetter(1))


# In[31]:


graph_closeness = nx.closeness_centrality(largest_subgraph)


# In[32]:


max_clo = max(graph_closeness.items(), key=itemgetter(1))


# In[33]:


graph_betweenness = nx.betweenness_centrality(largest_subgraph, normalized=True, endpoints=False)


# In[34]:


max_bet = max(graph_betweenness.items(), key=itemgetter(1))


# In[35]:


print(f"the node with id {max_de[0]} has a degree centrality of {max_de[1]:.2f} which is the maximum of the Graph")
print(f"the node with id {max_clo[0]} has a closeness centrality of {max_clo[1]:.2f} which is the maximum of the Graph")
print(f"the node with id {max_bet[0]} has a betweenness centrality of {max_bet[1]:.2f} which is the maximum of the Graph")


# Now, we can get to see how the Graph looks like. For that, we will use nx.drawing.layout to apply node positioning algorithms for the graph drawing. Specifically, we will use spring_layout that uses force-directed graph drawing which purpose is to position the nodes in two-dimensional space so that all the edges are of equal length and as few crossing edges as possible. It achieves this by assigning forces among the set of edges and nodes based on their relative positions and then uses this to simulate the motion of the edges and nodes. One of the parameters that we can adjust is k, the optimal distance between nodes; as we increase the value, the nodes will farther apart.  Once, that we got the positions, we are also going to create a special list so that we can draw the two nodes with higher centrality that we found in different colors to highlight them.

# In[39]:


node_and_degree = largest_subgraph.degree()
colors_central_nodes = ['orange', 'red']
central_nodes = ['331136088', '1191754450303623169']


# In[40]:


pos = nx.spring_layout(largest_subgraph, k=0.05)


# After all that calculation, we'll use the functions `.draw_networkx_nodes()` and `.draw()`. And finally, we have the drawing of the largest connected component of our original Graph:

# In[41]:


plt.figure(figsize = (20,20))
nx.draw(largest_subgraph, pos=pos, node_color=range(323), cmap=plt.cm.PiYG, edge_color="black", linewidths=0.3, node_size=60, alpha=0.6, with_labels=False)
nx.draw_networkx_nodes(largest_subgraph, pos=pos, nodelist=central_nodes, node_size=300, node_color=colors_central_nodes)
plt.savefig('graphfinal.png')
plt.show()





