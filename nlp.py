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

class StoreParser():
    
    def __init__(self):
        self.corenlp = StanfordCoreNLP()

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
            # Parse the document
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
                    count_dict[np] += 1
            with open(path, 'w') as file:
                for key in count_dict.iterkeys():
                    file.write(str(key) + "\t" + str(count_dict[key]) + "\n")
        return count_dict