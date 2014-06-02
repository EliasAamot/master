# -*- coding: utf-8 -*-
"""
Script to extract NP counts from the parsed papers.

@author: Elias
"""
import xml.etree.ElementTree as ET
import os
from nlp import TreeManipulator
from nltk.tree import Tree
import sortdict

def extract_nps():
    
    if not os.path.exists("NPs"):
        os.mkdir("NPs")
        
    for fil in os.listdir(os.path.join(os.getcwd(), "Parses")):
        # Do not reparse
        if os.path.exists(os.path.join("NPs", fil)):
            continue
        
        try:
            xml = ET.parse(os.path.join("Parses", fil))
        except:
            print fil
            exit()
        np_tally = sortdict.SortDict()
        # Go through all sentences
        for sentence in xml.iter('sentence'):
            # Find the mapping from word to lemma
            word_to_lemma_map = {}
            for token in sentence.iter('token'):
                word = token.find('word').text
                lemma = token.find('lemma').text
                word_to_lemma_map[word] = lemma
            # Extract NPs from the parse tree
            parse = sentence.find('parse')
            parse_string = parse.text
            parse_tree = Tree(parse_string)
            nps = TreeManipulator.get_all_np_variations(tree=parse_tree)
            # Map NPs to lemma forms
            for np in nps:
                np = map_to_lemma(np, word_to_lemma_map)
                np_tally[np] += 1
                
        # Store the tally of the file
        with open(os.path.join("NPs", fil), 'w') as npfile:
            for k,v in np_tally.iteritems():
                if not k in ["", " "]:
                    npfile.write(k+"\t"+str(v)+"\n")
        
def map_to_lemma(np, word_to_lemma_map):
    npl = []
    for word in np.split():
        try:
            npl.append(word_to_lemma_map[word])
        except:
            pass
    return ' '.join(npl)


if __name__=="__main__":
    extract_nps()