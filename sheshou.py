# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:27:25 2013

@author: elias
"""
import nlp
from methods import *
from collections import defaultdict
from operator import itemgetter

class Sheshou:
    
    def query(self, keywords):
#        self.find_a_count(keywords)
        print "Fetching abstracts for A-keywords..."
        abstracts = self.find_abstracts_for_keywords(keywords)
        print "Gathering NPs from abstracts..."
        nps = []
        for abstract in abstracts:
            nps.extend(nlp.find_np_chunks(abstract))
        print "Identifying most prominent NPs as B-terms..."
        cooc_dict = self.build_coocurrence_dictionary(nps)
        b_terms = list()
        for b_term in cooc_dict.iterkeys():
            b_terms.append( (b_term, cooc_dict[b_term]) )
        b_terms = sorted(b_terms, key=itemgetter(1))
        b_terms = b_terms[:-25] # Keep only the most significant
        print "Fetching C-terms from B-terms..."
        c_terms = defaultdict(int)
        for b in b_terms:
            b_abstracts = self.find_abstracts_for_keywords([b[0]])  
            nps = set()
            for abstract in b_abstracts:
                nps = nps.union(nlp.find_np_chunks(abstract))
            for np in nps:
                c_terms[np] += 1
        print "\n\nResults:"
        result_list = []
        for c_term in c_terms.iterkeys():
            result_list.append( (c_term, c_terms[c_term]) )
        result_list = sorted(result_list, key=itemgetter(1))
        for key, score in result_list[-25:]:
            print key, ":", score
            
    def find_abstracts_for_keywords(self, keywords):
        # Find unique IDs for the papers with the keywords
        all_ids = []
        for keyword in keywords:
            ids = get_ids_for_keyword(keyword)
            for id in ids:
                if not id in all_ids:
                    all_ids.append(id)
        # Find titles from ids
        titles = []        
        for id in all_ids:
            titles.extend(get_abstract_for_id(id))
        return titles
        
    def build_coocurrence_dictionary(self, nps):
        cooc = defaultdict(int)
        for np in nps:
            cooc[np] += 1
        return cooc
        
if __name__=="__main__":
    Sheshou().query(["raynaud","raynauds","raynaud's"])