# -*- coding: utf-8 -*-
"""
Script to preprocess papers from PLOS with Stanford Core NLP tools, giving
offset annotations for the papers in a separate file.

@author: elias
"""

from subprocess import call
import os

so_file = open("/home/elias/NTNU/nxml2txt/6.xml.so", 'r')
txt_file = open("/home/elias/NTNU/nxml2txt/6.xml.txt", 'r')

sos =[line.strip().split() for line in so_file]
text = txt_file.read()

def get_text(so):
    return text[int(so[2]):int(so[3])]

for so in sos:
    if so[1] == 'abstract':
        abst = get_text(so)
        with open("tmp/abst.txt.temp", 'w') as absfile:
            absfile.write(abst)
        call(["java","-cp","sfcnlp/stanford-corenlp-3.3.1.jar:sfcnlp/stanford-corenlp-3.3.1-models.jar:sfcnlp/xom.jar:sfcnlp/joda-time.jar:sfcnlp/jollyday.jar:sfcnlp/ejml-0.23.jar", "-Xmx3g", "edu.stanford.nlp.pipeline.StanfordCoreNLP", "-annotators", "tokenize,cleanxml,ssplit,pos,lemma,ner,parse,dcoref", "-output", "xml", "-file", "tmp/abst.txt.temp"])
        with open("tmp/abst.txt.temp.xml", 'r') as ppfile:
            content = ppfile.read()
        os.remove("tmp/abst.txt.temp.xml")    
        os.remove("tmp/abst.txt.temp")    
        print content