# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 15:04:58 2013

@author: elias
"""
from corenlp import StanfordCoreNLP
from nltk.tree import Tree
from collections import defaultdict
import medeley_fetch
import json
import regex, nltk
import pexpect

class StoreParser():
    
    def __init__(self):
        self.corenlp = StanfordCoreNLP()
        self.treemanipulator = TreeManipulator()
        self.stemmer = Stemmer()
        self.blacklist = [line.strip() for line in open("blacklist.txt", 'r')]

    def parse_abstract(self, id):
        count_dict = dict()
        if id in self.blacklist:
            print 'Id {0} is blacklisted.'.format(id)
            return count_dict
        path = "NPs/" + id + ".nps"
        try:
            with open(path, 'r') as file:
                for line in file:
                    line = line.strip()
                    split = line.split("\t")
                    stemmed_np = split[0]
                    count = split[1]
                    unstemmed = dict()
                    for i in xrange(2,len(split),2):
                        unstemmed[split[i]] = int(split[i+1])
                    count_dict[stemmed_np] = [int(count), unstemmed]
        except IOError:
            try:
                print "Parsing " + str(id)
                try:
                    abstract = medeley_fetch.get_abstract_for_id(id)
                except Exception as e:
                    if e.args[0] == "TooManyRequestsException":
                        print "Skipping due to server overload, consider halting program..."
                    elif e.args[0] == "PaperHasNoAbstractException":
                        print "Object has no abstract, probably not a paper..."
                    else: 
                        print "Unknown exception occured when fetching paper..."
                    return count_dict
                # Can happen due to server overload, but apparently for other reasons as well
                parse = self.corenlp.parse(abstract)
                document = json.loads(parse)
                with open("Parses/" + id + ".json", 'w') as file:
                    file.write(parse)
                # Extract all the nps from the parse trees
                # TODO: Not that important, I guess
                for sentence in document['sentences']:
                    parse_tree = sentence['parsetree']
                    nltk_tree = Tree(parse_tree)
                        
                    nps = self.treemanipulator.get_all_np_variations(nltk_tree)
                    for original_np in nps:      
                        if original_np != "":
                            stemmed_np = self.stemmer.stem_string(original_np)
                            if stemmed_np in count_dict.keys():
                                count_dict[stemmed_np][0] += 1
                                count_dict[stemmed_np][1][original_np] += 1
                            else:
                                count_dict[stemmed_np] = [1, defaultdict(int)]
                                count_dict[stemmed_np][1][original_np] = 1
                with open(path, 'w') as file:
                    for key in count_dict.iterkeys():
                        file.write(str(key) + "\t" + str(count_dict[key][0]) + "\t")
                        for original_np in count_dict[key][1].iterkeys():
                            file.write(str(original_np) + "\t" + str(count_dict[key][1][original_np]) + "\t")
                        file.write("\n")
            except pexpect.ExceptionPexpect:
                print "Timeout during parsing. Verify that the content is rubbish, and add to the blacklist..."
                exit()
        return count_dict
            
        
class TreeManipulator:
    """
        A collection of methods for manipulation and extraction from NLTK trees.
    """    
    
    def get_all_np_variations(self, tree=None):
        # Returns a list of all NP variations found in the sentece parse tree
        nps = self.extract_all(tree=tree, label='NP')
        all_nps = set()
        for np in nps:
            all_nps.add(self.get_string(np))
            all_nps.add(self.get_string(self.prune_tree(np, ['DT'])))
            all_nps.add(self.get_string(self.prune_tree(np, ['DT', 'JJ'])))
        return all_nps
        
    def extract_all(self, tree=None, label=''):
        # Extracts all subtrees with a given label from a tree
        return [subtree for subtree in tree.subtrees() if subtree.node==label]
    
    def prune_tree(self, tree=None, labels=[]):
        # Prunes away all children with one of the given labels.
        pruned_tree = tree.copy(deep=True)
        for i, child in enumerate(pruned_tree):
            if child.node in labels:
                pruned_tree.pop(i)
        return pruned_tree
        
    def get_string(self, tree=None):
        # Returns the normalized (lower-case) and stemmed string of the leaves of the tree
        words = [word for word in tree.leaves() if not word in ["-LRB-", "-RRB-"]]
        return regex.np_normalize(' '.join(words))
        
class Stemmer:
    """
        A wrapper around nltk's LancasterStemmer, which contains special rules for handling variants of "to be", as the Lancaster stemmer fails at that particular word.
    """
    def __init__(self):
        self.lancasterstemmer  = nltk.stem.LancasterStemmer()
        
    def stem(self, words):
        return ['be' if word.lower() in ['is', 'are', 'were', 'was'] else self.lancasterstemmer.stem(word) for word in words]

    def stem_string(self, string):
        return regex.np_normalize(' '.join(self.stem(string.split())))