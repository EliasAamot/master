# -*- coding: utf-8 -*-
"""
An Arrowsmith-like LBKD system utilizing the Stanford Core NLP Toolkit and the Medeley database.

@author: elias
"""
import nlp, medeley_fetch, sortdict
import math
from collections import defaultdict

def query(keyword):
    print "Selecting papers containing the A-keywords..."
    ids = medeley_fetch.get_ids_for_keyword(keyword)
    print "Gathering NPs from A abstracts..."
    count_dict = parse_abstracts(ids)
    print "Calculating TF-IDFs for potential B terms..."
    tfidfs = calcualte_tdidf(count_dict)
    print "Filtering potential B terms..."
    b_term_candidates = get_k_best_and_filter(tfidfs, 250, [word for word in keyword.split()])
#    for best in b_term_candidates:
#        print best, tfidfs[best]
    print "Please choose B-terms (write numbers seperated by comma, no spaces)..."    
    b_terms = choose_b_terms(b_term_candidates)
    print "Extracting C-term candidates from B-keywords..."
    b_dict = dict()
    for b_term in b_terms:
        ids = medeley_fetch.get_ids_for_keyword(b_term)
        count_dict = parse_abstracts(ids)
        tfidfs = calcualte_tdidf(count_dict)
        b_dict[b_term] = tfidfs[:25]
    print "Ranking C-term candidates..."
    c_terms = rank(b_dict)
    print "Printing final results..."
    for c_term in c_terms[:40]:
        print c_term
# 4,6,9,11,13,15,16,22,27,30,31,35
      
def parse_abstracts(ids):
    parser = nlp.StoreParser()
    all_counts = dict()
    for i, id in enumerate(ids):
        print i, "/", len(ids)
        if i > 250:
            break
        # Join the new counts with the total
        counts = parser.parse_abstract(id)
        for key in counts.iterkeys():
            if key in all_counts.keys():
                all_counts[key][0] += counts[key][0]
            else:
                all_counts[key] = [counts[key][0], defaultdict(int)]
            for orig_key in counts[key][1].keys():
                all_counts[key][1][orig_key] += counts[key][1][orig_key]
    return all_counts
        
def calcualte_tdidf(term_freqs):
    doc_freqs = dict()
    stem_to_full_translator = dict()
    for keyword in term_freqs.iterkeys():
        # Rmove all NPs that only occur once to avoid doing extra work
        if term_freqs[keyword][0] == 1:
            continue
        # For each stemmed cluster, find the most representative NP
        max_count = 0
        max_np = None
        for np in term_freqs[keyword][1].iterkeys():
            if term_freqs[keyword][1][np] > max_count:
                max_count = term_freqs[keyword][1][np]
                max_np = np
        stem_to_full_translator[keyword] = max_np
        doc_freqs[max_np] = medeley_fetch.get_count_for_keyword(max_np)
    # We estimate the document collection size based on the frequncy of the most common NP. 
    collection_size = max(doc_freqs.values())
    # Finally we have the information required to calculate TD-IDF
    tfidfs = sortdict.SortDict()
    for keyword in term_freqs.iterkeys():
        if term_freqs[keyword][0] == 1:
            continue
        term_freq = term_freqs[keyword][0]
        doc_freq = doc_freqs[stem_to_full_translator[keyword]]
        # Disregard phrases that occur less that two times; 
        # they cannot be used to connect unrelated diciplins anyway.
        if doc_freq < 2:
            tfidfs[stem_to_full_translator[keyword]] = 0.0
        else:
            idf = math.log(float(collection_size) / float(doc_freq), 2)
            tfidfs[stem_to_full_translator[keyword]] = float(term_freq)*idf
    return tfidfs
        
def get_k_best_and_filter(scores, k, filter_terms):
    sorted_keywords = scores[:]
    chosen = list()
    i = 0
    while i < k:
        check = sorted_keywords.pop(0)
        accept_it = True
        # Check if word is to be filtered out
        for filter_term in filter_terms:
            if filter_term in check:
                accept_it = False
        # If word is not to be filtered out, store it        
        if accept_it:
            i += 1
            chosen.append(check)
    return chosen
    
def choose_b_terms(candidates):
    for i, b_candidate in enumerate(candidates):
        print str(i) + ": " + b_candidate
    b_term_input = raw_input()
    b_term_input = b_term_input.split(",")
    return [candidates[int(b_index)] for b_index in b_term_input]

def rank(b_term_dict):
    c_term_dict = sortdict.SortDict()
    for b_term in b_term_dict:
        for c_candidate in b_term_dict[b_term]:
            c_term_dict[c_candidate] += 1   
    return c_term_dict

if __name__=="__main__":
    query("ocean acidification")