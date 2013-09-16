# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 13:35:29 2013

@author: elias
"""
import nltk
 
    
def find_np_chunks(text):
    grammar = "NP: {<JJ>+<NN|NNS|NNP>+ | <NN|NNS|NNP>+}"
    cp = nltk.RegexpParser(grammar)           
        
    nps = []
    tokens = nltk.wordpunct_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    chunked = cp.parse(tagged)
    for subtree in chunked.subtrees():
        if subtree.node == "NP":
            string = [leaf[0] for leaf in subtree.leaves()]
            nps.append(' '.join(string).strip().lower())
    return nps