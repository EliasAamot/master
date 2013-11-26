# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 14:25:40 2013

@author: elias
"""
import os, json, re
from corenlp import StanfordCoreNLP

def create_file():
    path = "Papers"
    relevant_abstracts = []
    
    for dir_entry in os.listdir(path):
        try:
            dir_entry_path = os.path.join(path, dir_entry)
            with open(dir_entry_path, 'r') as file:
                xml = json.loads(file.read())
                abstract = xml["abstract"]
                if any(word in abstract.lower() for word in ["gives", "increase", "reduce", "increases", "increased", "reduces", "reduced"]):
                    relevant_abstracts.append(abstract)
        except:
            pass
        
    with open('relabs.txt', 'w') as file:
        for rel in relevant_abstracts:
            rel = re.sub("\n", "", rel)
            rel = re.sub("\\n", "", rel)
            file.write(rel + "\n")

def parse_file():
    sentence_file = open('sentences.txt', 'w')
    dep_file = open('deps.txt', 'w')
    tree_file = open('trees.txt', 'w')
    abstracts = [line.strip() for line in open('relabs.txt', 'r')]
    corenlp = StanfordCoreNLP()
    for abstract in abstracts:
        parse = corenlp.parse(abstract)
        xml = json.loads(parse)
        sentences = xml['sentences']
        for sentence in sentences:
            # Write sentence
            sentence_file.write(sentence['text'] + "\n")
            # Write parse tree
            tree_file.write(sentence['parsetree'] + "\n")
            # Write dependencies
            for dep in sentence['dependencies']:
                dep_file.write('@'.join(dep) + "\t")
            dep_file.write("\n")
    dep_file.close()
    tree_file.close()
    sentence_file.close()
    
if __name__=="__main__":
    parse_file()