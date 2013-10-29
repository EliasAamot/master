# -*- coding: utf-8 -*-
"""
Simple methods for manipulating NLTK trees.

@author: elias
"""
import regex

# Returns a list of all NP variations found in the sentece parse tree
def get_all_np_variations(tree=None):
    nps = extract_all(tree=tree, label='NP')
    all_nps = set()
    for np in nps:
        all_nps.add(get_string(np))
        all_nps.add(get_string(prune_tree(np, ['DT'])))
        all_nps.add(get_string(prune_tree(np, ['DT', 'JJ'])))
    return all_nps
    
# Extracts all subtrees with a given label from a tree
def extract_all(tree=None, label=''):
    return [subtree for subtree in tree.subtrees() if subtree.node==label]

# Prunes away all children with one of the given labels.
def prune_tree(tree=None, labels=[]):
    pruned_tree = tree.copy(deep=True)
    for i, child in enumerate(pruned_tree):
        if child.node in labels:
            pruned_tree.pop(i)
    return pruned_tree
    
# Returns the normalized (lower-case) string of the leaves of the tree
def get_string(tree=None):
    return regex.np_normalize(' '.join(tree.leaves()))