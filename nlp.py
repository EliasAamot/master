# -*- coding: utf-8 -*-
"""
A collection of tools for basic information extraction from text abstracts, using NLTK.

@author: Elias Aamot
"""
import nltk

def preprocess(text):
    tokens = nltk.wordpunct_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    return tagged
    
def chunk_nps(tagged_words):
    grammar = "NP: {<JJ>+<NN|NNS|NNP>+ | <NN|NNS|NNP>+}"
    cp = nltk.RegexpParser(grammar)           
    chunked = cp.parse(tagged_words)
    nps = list()
    for subtree in chunked.subtrees():
        if subtree.node == "NP":
            string = [leaf[0] for leaf in subtree.leaves()]
            nps.append(' '.join(string).strip().lower())
    return nps

def find_np_chunks(text):
	return chunk_nps(preprocess(text))

if __name__=="__main__":
    pass
