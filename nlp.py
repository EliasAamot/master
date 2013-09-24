# -*- coding: utf-8 -*-
"""
A collection of tools for basic information extraction from text abstracts,
using NLTK.

Together the methods form a pipeline, converting raw text to extracted 
relations.

Pipeline:
    preprocess (Raw text -> pos-tagged words)
    chunk_nps (pos-tagged words -> np-chunked sentence tree)
    extract_relations (np-chunked sentence tree -> relations)

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
    return cp.parse(tagged_words)
#    for subtree in chunked.subtrees():
#        if subtree.node == "NP":
#            string = [leaf[0] for leaf in subtree.leaves()]
#            nps.append(' '.join(string).strip().lower())
#    return nps
    
def extract_relations(chunked_sentence):
    print chunked_sentence

def text_to_relations(text):
    tagged = preprocess(text)
    chunked = chunk_nps(tagged)
    relations = extract_relations(chunked)
    return relations

if __name__=="__main__":
    print chunk_nps(preprocess("Mr. John Smith is a good guy."))
#    text_to_relations("Recent studies demonstrate that volcanic ash has the potential to increase phytoplankton biomass in the open ocean. However, besides fertilizing trace metals such as Fe.")