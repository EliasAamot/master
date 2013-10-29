# -*- coding: utf-8 -*-
"""
An Arrowsmith-like LBKD system utilizing the Stanford Core NLP Toolkit.

@author: elias
"""
from corenlp import StanfordCoreNLP
from nltk.tree import Tree
import url_fetch
import treemanipulation
import sortdict
import json

class Stanshou:
    
    def query(keywords):
        print "Storing abstracts for A-keywords..."
        ids = Stanshou.get_ids(keywords)
        print "Gathering NPs from abstracts..."
        count_dict = Stanshou.parse_abstracts(ids)
        
        # print it all
        with open('results.txt', 'w') as resultfile:
            for key in count_dict[:]:
                resultfile.write(key + ":" +  str(count_dict[key]) + "\n")
        
    def parse_abstracts(ids):
        corenlp = StanfordCoreNLP()
        count_dict = sortdict.SortDict()

        for id in ids:
            # Parse the document
            abstract = url_fetch.get_abstract_for_id(id)
            parse = corenlp.parse(abstract)
            document = json.loads(parse)
            # Extract all the nps from the parse trees
            for sentence in document['sentences']:
                parse_tree = sentence['parsetree']
                nltk_tree = Tree(parse_tree)
                
                nps = treemanipulation.get_all_np_variations(nltk_tree)
                for np in nps:      
                    count_dict[np] += 1
        return count_dict
            
    def get_ids(keywords):
        # Find unique IDs for the papers with the keywords
        all_ids = set()
        for keyword in keywords:
            ids = url_fetch.get_ids_for_keyword(keyword)
            all_ids = all_ids.union(ids)
        return all_ids

if __name__=="__main__":
    Stanshou.query(["raynaud","raynauds","raynaud's"])
