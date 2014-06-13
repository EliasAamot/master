# -*- coding: utf-8 -*-
"""
Script to extract NP counts from the parsed papers.

@author: Elias
"""
import xml.etree.ElementTree as ET
import os, subprocess
from nlp import TreeManipulator
from nltk.tree import Tree
import sortdict
import medeley_fetch
import codecs

coreNLPpath = "/home/elias/tmp/master/sfcnlp"
outfolder = "Parses"

def extract_nps_for_all():
    
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
            
        np_tally = tally_xml(xml)
                
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
    
def tally_xml(xml):
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
            
    return np_tally

def extract_nps_single_paper(iid):
    
    if not os.path.exists("NPs"):
        os.mkdir("NPs")
    
    if not os.path.exists(os.path.join("Parses", iid+".xml")):
        parse_abstract(iid)
     
    xml = ET.parse(os.path.join("Parses", iid+".xml"))
    np_tally = tally_xml(xml)
    
    with codecs.open(os.path.join("NPs", iid+".xml"), mode='w', encoding='utf-8') as npfile:
        for k,v in np_tally.iteritems():
            if not k in ["", " "]:
                npfile.write(k+"\t"+str(v)+"\n")
    
def parse_abstract(iid):
    # Get abstract
    abstract = medeley_fetch.Fetcher().get_abstracts_for_id(iid)
    
    # Write abstract to tmp file
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    
    with codecs.open("tmp/"+iid+".tmp", mode='w', encoding='utf-8') as tofile:
        if abstract != None:
            tofile.write(abstract)
    
    # Parse it
    subprocess.call(["java", "-cp", 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1.jar") + ":" + 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1-models.jar") + ":" + 
          os.path.join(coreNLPpath, "xom.jar") + ":" + 
          os.path.join(coreNLPpath, "joda-time.jar") + ":" + 
          os.path.join(coreNLPpath, "jollyday.jar") + ":" + 
          os.path.join(coreNLPpath, "ejml-0.23.jar"), 
          "-Xmx3g","edu.stanford.nlp.pipeline.StanfordCoreNLP",
          "-annotators", "tokenize,cleanxml,ssplit,pos,lemma,parse",
          "-outputExtension", ".xml", "-replaceExtension", "-outputDirectory", outfolder, 
          "-file", "tmp/"+iid+".tmp"])
          

if __name__=="__main__":
    extract_nps_for_all()