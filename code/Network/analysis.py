
### Initial loads
import networkx as nx, numpy as np
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
from time import strftime
from operator import itemgetter
import sys, json, pickle, codecs
sys.path.append("../models/")
from ModelBase import Status, SessionFactory

def unpickle_struc(f=""):
    fin = open(f, "r")
    d = pickle.load(fin)
    return d

def barplot(struc, N=20, title=""):
    width = .25 # The width of the bars
    ind = np.arange(N) # The x location for the groups
    labels = [unicode(n[0]) for n in struc[0:N]]
    values = [n[1] for n in struc[0:N]]
    fig, ax = plt.subplots()
    rects = ax.bar(ind, values, width, color='b')
    ax.set_ylabel('Count')
    ax.set_title(title)
    ax.set_xticks(ind+width)
    ax.set_xticklabels(labels, rotation="vertical")
    plt.subplots_adjust(bottom=.35)
    plt.show()


DG = unpickle_struc("20141206-193857_1_directed_graph.dat")
BG = unpickle_struc("20141206-193857_2_bipartite_graph.dat")
hashtags = unpickle_struc("20141207-095748_3_hashtags.dat")

### Directed graph

# To trim the directed graph to only include nodes with a weight of > 2
outdeg = DG.out_degree()
mDG = [n for n in outdeg if outdeg[n] > 100]
mDG = DG.subgraph(mDG)

# OR # 

indeg = DG.in_degree()
mDG = [n for n in indeg if indeg[n] > 100]
mDG = DG.subgraph(mDG)

# Draw the graph
pos = nx.spring_layout(mDG)
nx.draw_networkx_nodes(mDG, pos, node_size=100)
nx.draw_networkx_edges(mDG, pos, width=1, alpha=.2)
nx.draw_networkx_labels(mDG,pos,font_size=12,font_family='sans-serif')
plt.axis('off')
plt.show()

# Get the most frequently mentioned users
mentioned = sorted(DG.degree_iter(), key=itemgetter(1),reverse=True)
# And plot the most frequently mentioned
barplot(mentioned, N=30, title="30 most frequently mentioned users")

# Calculate betweenness centrality of all nodes
betweenness = nx.betweenness_centrality(mDG)
# Sort betweenness in descending order
s_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
barplot(s_betweenness, N=30, title="30 users with the highest betweenness scores")
# Calculate the closeness centrality of all nodes
closeness = nx.closeness_centrality(mDG)
s_closeness = sorted(closeness.items(), key=lambda x: x[1], reverse=True)
barplot(s_closeness, N=30, title="30 users with the highest closeness scores")

### End directed graph


# Open the hashtags, sort by descending order of frequency, and plot
hashtags = unpickle_struc("20141207-095748_3_hashtags.dat")
s_hashtags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
barplot(s_hashtags, N=30, title="30 most frequent hashtags")


