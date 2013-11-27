# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 16:14:44 2013

@author: elias
"""
import nltk
import networkx as nx
import matplotlib.pyplot as plt
import copy

def re_dp(patterns):
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
                
            for pattern in patterns:
                matches = RelationPatternMatcher(pattern).match(G)
                for match in matches:
                    # Then we have to try to find the phrases
                    sentence_tree = nltk.Tree(tree_lines[x])
                    # OPTIMIZATION POTENTIAL: Only locate phrases that are "terminal" i.e. in the output
                    variable_phrases = dict()
                    for v_name, v_value in match.items():
                        # Assumes that the heads word are unique...
                        leaf_position = sentence_tree.leaves().index(v_value)
                        tree_position = sentence_tree.leaf_treeposition(leaf_position)
                        # TODO improve finding of phrases, maybe using concepts
                        phrase = sentence_tree[tree_position[:-2]]
                        string = ' '.join(phrase.leaves()).strip()
                        variable_phrases[v_name]= string                                             
                     
                    # Finally print output of pattern
                    output = pattern.output
                    for v_name, v_phrase in variable_phrases.items():
                        output = output.replace(v_name, v_phrase)
                    print
                    print output
                    print sentence_lines[x]
                    print


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

    nx.draw_networkx_edge_labels(G, graph_pos, edge_labels=edge_labs, font_size=node_text_size,
                            font_family=text_font)

    # show graph
    plt.show()

class RelationPatternMatcher:
    
    def unify(self, v1, v2):
        """
            Tries to unify two sets of variable assignments, V1 and V2. 
            Returns the unification if there are no variables with different
            values, None otherwise.
        """
        # OPTIMIZATION POTENTIAL?
        unification = copy.copy(v1)
        for key, value in v2.items():
            if not key in unification:
                unification[key] = value
            elif value != unification[key]:
                return None
        return unification
                
    def generate_candidates(self, matchings):
        """
            Generates a list of variable assignments derived from the 
            matching candidates provided.
        """
        candidates = []
        variable1 = matchings[0][1]
        variable2 = matchings[0][2]
        
        for matching_candidate in matchings[1]:
            candidate = dict()
            candidate[variable1] = matching_candidate[0]
            candidate[variable2] = matching_candidate[1]
            candidates.append(candidate)
        return candidates    
    
    def __init__(self, relation_pattern):
        self.relation_pattern = relation_pattern
        self.edge_matchings = dict([(edge_matcher, []) for edge_matcher in relation_pattern.edge_matchers])
        self.node_matchings = dict([(node_matcher, False) for node_matcher in relation_pattern.node_matchers])

    def match(self, graph):
        complete_matches = []
        
        # Generate matching candidates
        for edge in graph.edges_iter(data=True):
            for edge_matcher in self.relation_pattern.edge_matchers:
                if edge[2]['label'] in edge_matcher[0]:
                    self.edge_matchings[edge_matcher].append(edge)
        for node in graph.nodes_iter(data=False):
            for node_matcher in self.relation_pattern.node_matchers:
                if node in node_matcher[1]:
                    self.node_matchings[node_matcher] = True
                    
        # If any node or edge is unmatched, matching is impossible
        if not (all(self.node_matchings.values()) and all(self.edge_matchings.values())):
            return []
            
        else:            
            # The next problem is to find all complete matches (if any) in 
            # match candidate space. This requires a search.
            
            # OPTIMIZATION POTENTIAL: Pick the smallest one EM set to start with
#            print self.edge_matchings
#            print self.node_matchings
      
            stack = [(candidate, 1) for candidate in self.generate_candidates(self.edge_matchings.items()[0])]
            
            # Conduct search
            while stack:
#                print "SEARCH_STACK: " + str(stack)
                current_variables, next_i = stack.pop(0)
                # If we have checked all the edge matchers, do node matching
                if next_i >= len(self.edge_matchings):
                    full_node_match = all(current_variables[node_matcher[0]] in node_matcher[1] for node_matcher in self.relation_pattern.node_matchers)
                    if full_node_match:
                        complete_matches.append(current_variables)
                    else:
                        pass # Discard search fork as unproductive
                # Otherwise, match against new potential edge matchers
                else:                
                    for candidate in self.generate_candidates(self.edge_matchings.items()[next_i]):
                        # Check to see if the new variable constraints unify with the existing constraints
                        new_variables = self.unify(current_variables, candidate)
                        if new_variables: # Unification successful, keep going
                            stack.append( (new_variables, next_i+1) )
                            
            return complete_matches
                        
class RelationPattern:
    def __init__(self):
        self.edge_matchers = []
        self.node_matchers = []
        self.output = None
        self.name = None
    
    def add_edge_matcher(self, edge_matcher):
        self.edge_matchers.append(edge_matcher)

    def add_node_matcher(self, node_matcher):
        self.node_matchers.append(node_matcher)
        
    def __repr__(self):
        return '[RelationPattern "{0}"]'.format(self.name)
    

class RelationPatternFactory:

    def __init__(self, filename):
        self.relation_patterns = []
        self.build_from_file(filename)
        
    def build_from_file(self, filename):
        current_pattern = None
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                # Skip comments and blank lines
                if len(line)==0 or line[0] == "#":
                    continue 
                splits = line.split()
                if splits[0].upper() == "OUTPUT":
                    current_pattern.output = ' '.join(splits[1:]).strip()
                elif splits[0].upper() == "PATTERN":
                    # This is the begining of a new pattern
                    if current_pattern != None:
                        self.relation_patterns.append(current_pattern)
                    current_pattern = RelationPattern()
                    current_pattern.name = ' '.join(splits[1:]).strip()
                elif len(splits) == 3:
                    # This is a edge matcher
                    relations = tuple(splits[0].split("|"))
                    matcher = (relations, splits[1], splits[2])
                    current_pattern.add_edge_matcher(matcher)
                elif len(splits) == 2:
                    # This is a node matcher
                    words = tuple(splits[1].split("|"))
                    matcher = (splits[0], words)
                    current_pattern.add_node_matcher(matcher)
                else:
                    print 'Command "{0}" not recongized in line: {1}'.format(splits[0], line)   
        self.relation_patterns.append(current_pattern)
        
    def build(self):
        return self.relation_patterns
    
if __name__=="__main__":
    patterns = RelationPatternFactory("patterns.txt").build()
    re_dp(patterns)
    
