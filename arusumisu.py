# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 14:12:49 2013

@author: Elias
"""
from collections import defaultdict
from operator import itemgetter
from methods import *

PUBMED_SIZE = 23000000
CUTOFF_RATE = 1.0


class Arusumisu:

    def __init__(self):
        self.build_stopword_list()
        
    def query(self, keywords):
        self.find_a_count(keywords)
        print "Fetching titles for A-keywords..."
        titles = self.find_titles_for_keywords(keywords)
        print "Building co-occurrence dictionary..."
        cooc_dict = self.build_coocurrence_dictionary(titles)
        print "Identifying B-terms..."
        b_terms = self.find_b_terms(cooc_dict)
        print "Fetching C-terms from B-terms..."
        c_terms = defaultdict(int)
        for  b in b_terms:
            b_titles = self.find_titles_for_keywords([b])            
            title_words = set()
            for title in b_titles:
                words = title.split().strip()
                words = [normalize(word) for word in words]
                title_words = title_words.union(words)
            for word in title_words:
                c_terms[word] += 1
        print "\n\nResults:"
        result_list = []
        for c_term in c_terms.iterkeys():
            result_list.append( (c_term, c_terms[c_term]) )
        result_list = sorted(result_list, key=itemgetter(1))
        for key, score in result_list[-10:]:
            print key, ":", score
            
    def find_a_count(self, keywords):
        self.a_count = 0
        for keyword in keywords:
            self.a_count += get_count_for_keyword(keyword)
            
    def find_titles_for_keywords(self, keywords):
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
            titles.append(get_title_for_id(id))
        return titles
    
    def build_stopword_list(self):
        self.stopwords = []
        # Build stop-word list
        with open("stopwords.txt",'r') as file:  
            for line in file:
                line = line.strip()
                self.stopwords.append(line)
    
    def build_coocurrence_dictionary(self, titles):
        cooc = defaultdict(int)
        for title in titles:
            for word in title.split():
                # Normalize
                word = normalize(word)
                if not len(word):
                    continue
                # Remove stopwords
                if word in self.stopwords:
                    continue
                # Then add to dictionary
                cooc[word] += 1
        return cooc
    
    def find_b_terms(self, cooc): 
        b_terms = list()
        for term in cooc.iterkeys():
            if self.is_statistically_significant(term, cooc):
                b_terms.append(term)
        return b_terms
    
    def is_statistically_significant(self, term, cooc):
        # See if frequency is larger than frequency in pubmd
        B_count = get_count_for_keyword(term)
        A_freq = float(cooc[term])/float(self.a_count)
        pubmed_freq = float(B_count)/PUBMED_SIZE
        return (pubmed_freq/A_freq >= CUTOFF_RATE)
        
if __name__ == "__main__":
    a = Arusumisu()
    a.query(["raynaud","raynauds","raynaud's"])