#!/usr/bin/env python 

import networkx as nx, numpy as np
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
from time import strftime
import sys, json, pickle, codecs
sys.path.append("../models/")
from ModelBase import Status, SessionFactory

# Load the data
session = SessionFactory()
now = strftime("%Y%m%d-%H%M%S")

def pickle_struc(f="", d={}):
    fout = open(f, "w")
    pickle.dump(d, fout)
    return True

def unpickle_struc(f=""):
    fin = open(f, "r")
    d = pickle.load(fin)
    return d

def page_query(q):
    offset = 0
    while True:
        r = False
        for elem in q.limit(1000).offset(offset):
           r = True
           yield elem
        offset += 1000
        if not r:
            break

# The directed graph represents the mention network between twitter users
def create_graphs():
    # The directed graph represents an attention network between users
    DG = nx.DiGraph()
    # The bipartite graph will represent connections between users, separated by hashtag use
    BG = nx.Graph()
    # hashtags will be a simple counter of hashtag use
    hashtags = {}
    # Iterate over the data to create the graph

    i = 0
    for tweet in page_query(session.query(Status)):
        #if i == 1000:
        #    break
        if i % 50000 == 0:
            print(strftime("%Y-%m-%d %H:%M:%S") + ": Completed tweets - " + str(i))
        i += 1
        js = json.loads(json.dumps(tweet.rawjson))
        # For each of the retweets of this tweet, create a directed edge between the two twitter users
        if type(js) is not dict:
            continue
        # Source user's name
        u1 = js["user"]["screen_name"]
        # Add all mentions as a directed edge between two nodes
        for mention in js["entities"]["user_mentions"]:
            # mentioned user's name
            u2 = mention["screen_name"]
            # Add the edge between users for each mention - increment weight if it's been mentioned before
            if DG.has_edge(u1, u2):
                # Edge already exists, increment the weight
                DG[u1][u2]["weight"] += 1
            else:
                # New edge, add with weight=1
                DG.add_edge(u1, u2, weight=1)
        for hashtag in js["entities"]["hashtags"]:
            # The tag used
            tag = hashtag["text"]
            # Add to the counter
            if tag in hashtags:
                hashtags[tag] += 1
            else:
                hashtags[tag] = 1
            # Add the edge between the user and the hashtag - increment weight if it's been tagged before
            if BG.has_edge(u1, tag):
                # Edge already exists, increment the weight
                BG[u1][tag]["weight"] += 1
            else:
                # New edge with weight 1, make sure to set the bipartite attribute to separate node types
                BG.add_node(u1, bipartite=0)
                BG.add_node(tag, bipartite=1)
                BG.add_edge(u1, tag, weight=1)
    # Store the graph data, attempt to save an image of the graph
    pickle_struc(f=now + "_1_directed_graph.dat", d=DG)
    pickle_struc(f=now + "_2_bipartite_graph.dat", d=BG)
    pickle_struc(f=now + "_3_hashtags.dat", d=hashtags)
    nx.draw_circular(DG)
    plt.savefig(now + "_directed_graph_circular.png")
    #nx.draw(DG)
    #plt.savefig(now + "_directed_graph.png")
    #nx.draw_spectral(DG)
    #plt.savefig("directed_graph_spectral.png")
    #nx.draw_random(DG)
    #plt.savefig("directed_graph_random.png")
    return DG


if __name__ == "__main__":
    # Get the directed graph, text output of highest betweenness and closeness scores
    print(strftime("%Y-%m-%d %H:%M:%S") + ": starting analysis of twitter networks")
    DG = create_graphs()
    print(strftime("%Y-%m-%d %H:%M:%S") + ": completed twitter network analysis")


