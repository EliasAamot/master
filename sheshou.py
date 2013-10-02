# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 11:27:25 2013

@author: elias
"""
import nlp
from url_fetch import *
from collections import defaultdict
from operator import itemgetter

#PUBMED_SIZE = 23000000
PUBMED_SIZE = 5000000 #1985 size
CUTOFF_RATE = 1.0

class Sheshou:
    
    def query(self, keywords):
        self.find_a_count(keywords)
        print "Fetching abstracts for A-keywords..."
        abstracts = self.find_abstracts_for_keywords(keywords)
        print "Gathering NPs from abstracts..."
        nps = []
        for abstract in abstracts:
				nps.extend(nlp.find_np_chunks(abstract))
        print "Building co-occurrence dictionary..."
        cooc_dict = self.build_coocurrence_dictionary(nps)
        print "Identifying B-terms..."
        b_terms = self.find_b_terms(cooc_dict)
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

    def find_b_terms(self, cooc):        
        b_terms = list()
        for b_term in cooc.iterkeys():
            if self.is_statistically_significant(b_term, cooc):
                b_terms.append( (b_term, cooc[b_term]) )
        b_terms = sorted(b_terms, key=itemgetter(1))
        return b_terms
        
    def is_statistically_significant(self, term, cooc):
        # See if frequency is larger than frequency in pubmd
        B_count = get_count_for_keyword(term)
        A_freq = float(cooc[term])/float(self.a_count)
        pubmed_freq = float(B_count)/PUBMED_SIZE
        return (pubmed_freq/A_freq >= CUTOFF_RATE)

    def find_a_count(self, keywords):
        self.a_count = 0
        for keyword in keywords:
            self.a_count += get_count_for_keyword(keyword)

if __name__=="__main__":
    Sheshou().query(["raynaud","raynauds","raynaud's"])
