# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:14:44 2013

@author: elias
"""
import nltk
import networkx as nx
import matplotlib.pyplot as plt

def re_dp():
    with open('deps.txt', 'r') as file:
        dep_lines = [line.strip() for line in file]
    with open('trees.txt', 'r') as file:
        tree_lines = [line.strip() for line in file]
    with open('sentences.txt', 'r') as file:
        sentence_lines = [line.strip() for line in file]
    
    for x in xrange(min([len(dep_lines), len(tree_lines), len(sentence_lines)])):                    
            deps = dep_lines[x].split("\t")
            deps = [dep.split("@") for dep in deps]

            G = nx.DiGraph()
            for dep in deps:
                G.add_edge(dep[1], dep[2], label=dep[0])
            
            for edge in G.edges_iter(data=True):
                found1 = False; found2 = False

                for word in ["increases", "increased", "increase", "increasing"]:
                    if edge[1] == word:
                        found1 = True
                for word in ["resulted", "result", "results", "resulting"]:
                    if edge[0] == word:
                        found2 = True
                if (found1 and found2 and edge[2]['label']!="nsubj"):
#                if (found1 and found2):
                    anchor1 = edge[0]
                    anchor2 = edge[1]
                    label = edge[2]['label']
                    # Find the X and Y head words
                    x_head = None; y_head = None
                    for edge in G.out_edges(anchor2, data=True):
                        if edge[2]['label'] == "prep_in":
                            x_head = edge[1]
                    for edge in G.out_edges(anchor1, data=True):
                        if edge[2]['label'] == "nsubj":
                            y_head = edge[1]
                    if x_head and y_head:
                        sentence_tree = nltk.Tree(tree_lines[x])
                        # Assumes that the heads word are unique...
                        x_leaf_position = sentence_tree.leaves().index(x_head)
                        x_tree_position = sentence_tree.leaf_treeposition(x_leaf_position)
                        x_phrase = sentence_tree[x_tree_position[:-2]]
                        x_string = ' '.join(x_phrase.leaves()).strip()                        
                        
                        y_leaf_position = sentence_tree.leaves().index(y_head)
                        y_tree_position = sentence_tree.leaf_treeposition(y_leaf_position)
                        y_phrase = sentence_tree[y_tree_position[:-2]]
                        y_string = ' '.join(y_phrase.leaves()).strip()                        
                        
                        print "+{0} -> +{1}".format(y_string, x_string)
                        print sentence_lines[x]
                        print label
                        
                        draw_graph(G)
      


def draw_graph(G, labels=None, graph_layout='shell',
               node_size=1600, node_color='blue', node_alpha=0.3,
               node_text_size=12,
               edge_color='blue', edge_alpha=0.3, edge_tickness=1,
               edge_text_pos=0.3,
               text_font='sans-serif'):
                   
    # these are different layouts for the network you may try
    # shell seems to work best
    if graph_layout == 'spring':
        graph_pos=nx.spring_layout(G)
    elif graph_layout == 'spectral':
        graph_pos=nx.spectral_layout(G)
    elif graph_layout == 'random':
        graph_pos=nx.random_layout(G)
    else:
        graph_pos=nx.shell_layout(G)

    # draw graph
    nx.draw_networkx_nodes(G,graph_pos,node_size=node_size, 
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G,graph_pos,width=edge_tickness,
                           alpha=edge_alpha,edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos, font_size=node_text_size,
                            font_family=text_font)
                            
    edge_labs=dict([((u,v,),d['label'])
             for u,v,d in G.edges(data=True)])     
    print edge_labs                           
    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labs, font_size=node_text_size,
                            font_family=text_font)

    # show graph
    plt.show()


def re_pt():
    with open('trees.txt', 'r') as file:
        for i, line in enumerate(file):
            tree = nltk.Tree(line.strip())
            
            # Discovery pattern 1
            
            # 1.1 Look for increase(s/d)
            treepath = None
            for j, leaf in enumerate(tree.leaves()):
                if leaf.lower() == "increase" or leaf.lower() == "increases" or leaf.lower() == "increased":
                    treepath = tree.leaf_treeposition(j)
            
            # 1.2 Verify that the detected object is a verb
            x = None; y = None
            if treepath != None:
                # Check the node above the leaf
                node = tree[treepath[:-1]]
                if "VB" in node.node:
                    # 1.3 X = V///NP\
                    subtree = tree[treepath[:-3]]
                    for daughter in subtree:
                        if daughter.node == "NP":
                            x = ' '.join(daughter.leaves()).strip()
                    # 1.4 Y = V//NP\
                    subtree = tree[treepath[:-2]]
                    for daughter in subtree:
                        if daughter.node == "NP":
                            y = ' '.join(daughter.leaves()).strip()
            # 1.5 Print discovery if any
            if x and y:
                print "+({0}) -> +({1}) / {2}".format(str(x), str(y), i)
            
if __name__=="__main__":
    re_dp()