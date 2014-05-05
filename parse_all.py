# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 10:51:20 2014

@author: elias
"""
import os, subprocess

def parse():
    filefolder = "NPapers"
    coreNLPpath = "/home/elias/master/sfcnlp"
    outfolder = "NParses"
    
    # Create list of files to parse    
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
    
    filenames = [os.path.join(filefolder, filename) for filename in os.listdir(filefolder) if '.txt' in filename]
    
    with open(os.path.join("tmp", "corenlpfilelist"), 'w') as file:
        for filename in filenames:
            file.write(filename + "\n")

    # Run CoreNLP on list of files
    subprocess.call(["java", "-cp", 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1.jar") + ":" + 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1-models.jar") + ":" + 
          os.path.join(coreNLPpath, "xom.jar") + ":" + 
          os.path.join(coreNLPpath, "joda-time.jar") + ":" + 
          os.path.join(coreNLPpath, "jollyday.jar") + ":" + 
          os.path.join(coreNLPpath, "ejml-0.23.jar"), 
          "-Xmx3g","edu.stanford.nlp.pipeline.StanfordCoreNLP",
          "-annotators", "tokenize,cleanxml,ssplit,pos,lemma,parse", "-ssplit.eolonly", "-newlineIsSentenceBreak"
          "-outputExtension", ".xml", "-replaceExtension", "-outputDirectory", outfolder, 
          "-filelist", os.path.join("tmp", "corenlpfilelist")])
          

if __name__ == "__main__":
    parse()