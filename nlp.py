# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:04:58 2013

@author: elias
"""
from corenlp import StanfordCoreNLP
from nltk.tree import Tree
import sortdict
import treemanipulation
import medeley_fetch
import json
import regex, nltk

class StoreParser():
    
    def __init__(self):
        self.corenlp = StanfordCoreNLP()
        self.treemanipulator = TreeManipulator()

    def parse_abstract(self, id):
        count_dict = sortdict.SortDict()
        path = "Data/" + id + ".nps"
        
        try:
            with open(path, 'r') as file:
                for line in file:
                    line = line.strip()
                    np, count = line.split("\t")
                    count_dict[np] = count
        except IOError:
            print "Parsing " + str(id)
            abstract = medeley_fetch.get_abstract_for_id(id)
            # Can happen due to server overload
            if abstract == None:
                return count_dict
            parse = self.corenlp.parse(abstract)
            document = json.loads(parse)
            # Extract all the nps from the parse trees
            for sentence in document['sentences']:
                parse_tree = sentence['parsetree']
                nltk_tree = Tree(parse_tree)
                    
                nps = treemanipulation.get_all_np_variations(nltk_tree)
                for np in nps:      
                    if np != "":
                        count_dict[np] += 1
            with open(path, 'w') as file:
                for key in count_dict.iterkeys():
                    file.write(str(key) + "\t" + str(count_dict[key]) + "\n")
        return count_dict
class TreeManipulator:
    
    def __init__(self):
        self.stemmer = Stemmer()
    
    # Returns a list of all NP variations found in the sentece parse tree
    def get_all_np_variations(self, tree=None):
        nps = self.extract_all(tree=tree, label='NP')
        all_nps = set()
        for np in nps:
            all_nps.add(self.get_string(np))
            all_nps.add(self.get_string(self.prune_tree(np, ['DT'])))
            all_nps.add(self.get_string(self.prune_tree(np, ['DT', 'JJ'])))
        return all_nps
        
    # Extracts all subtrees with a given label from a tree
    def extract_all(self, tree=None, label=''):
        return [subtree for subtree in tree.subtrees() if subtree.node==label]
    
    # Prunes away all children with one of the given labels.
    def prune_tree(self, tree=None, labels=[]):
        pruned_tree = tree.copy(deep=True)
        for i, child in enumerate(pruned_tree):
            if child.node in labels:
                pruned_tree.pop(i)
        return pruned_tree
        
    # Returns the normalized (lower-case) and stemmed string of the leaves of the tree
    def get_string(self, tree=None):
        words = tree.leaves()
        stemmed = self.stemmer.stem(words)
        return regex.np_normalize(' '.join(stemmed))
        
class Stemmer:
    """
        A wrapper around nltk's LancasterStemmer, which contains special rules for handling variants of "to be", as the Lancaster stemmer fails at that particular word.
    """
    def __init__(self):
        self.lancasterstemmer  = nltk.stem.LancasterStemmer()
        
    def stem(self, words):
        return ['be' if word.lower() in ['is', 'are', 'were', 'was'] else self.lancasterstemmer.stem(word) for word in words]
