# -*- coding: utf-8 -*-
"""
Script to run Stanford Parsers in concurrently. 

@author: elias
"""
import multiprocessing
import os, subprocess
import time, json

outfolder = "Parses"
coreNLPpath = "/home/elias/tmp/master/sfcnlp"
filefolder = "Abstracts"
raw_folder = "Data"

number_of_processes = 12
    
def parse(filelist):
    # Run CoreNLP on list of files
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
          "-filelist", filelist])
          

def build_tmp_files():
    # Find all unparsed papers
    already_parsed = set([filename[:-4] for filename in os.listdir(os.join(os.getcwd(), outfolder))])
    filenames = [os.path.join(filefolder, filename+".txt") for filename in os.listdir(os.join(os.getcwd(), filefolder)) if not filename[:-4] in already_parsed]

    # Split them into $number_of_processes partitions of similar size
    partitions = []    
    
    partition_size = len(filenames) / number_of_processes
    for i in xrange(0, len(filenames), partition_size):
        partition = filenames[i:i+partition_size]
        partitions.append(partition)
        
    # Distribute the remaining elements evenly among the processes
    remainder = partitions.pop()
    i = 0
    while remainder:
        element = remainder.pop()
        partitions[i].append(element)
        i += 1
        if i > len(remainder):
            i = 0
            
    # Write the partitions to tmp file lists
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")
        
    for i, partition in enumerate(partitions):
        with open("tmpfile"+str(i), 'w') as tmpfile:
            for filename in partition:
                tmpfile.write(filename+"\n")

def extract_abstracts():
    if not os.path.isdir(filefolder):
        os.mkdir(filefolder)
    
    existing_abstracts = set([filename[:-4] for filename in os.listdir(os.path.join(os.getcwd(), filefolder))])
    for filename in os.listdir(os.path.join(os.getcwd(), raw_folder)):
	if filename[-3:] == ".cnt" or filename[:-4] in existing_abstracts:
	    continue
        if not filename[:-4] in existing_abstracts:
            with open(os.path.join(raw_folder, filename+".txt"), 'r') as filen:
                xml = json.loads(filen)
                abstract = xml['abstract']
            with open(os.path.join(filefolder, filename+".txt"), 'w') as filen:
                filen.write(abstract)
    
if __name__ == "__main__":
    extract_abstracts()    
    build_tmp_files()
    
#    print "Starting parsing at " + time.strftime("%c")
#    pool = multiprocessing.Pool(processes=number_of_processes)
#    for i in xrange(number_of_processes):
#        parse(os.path.join("tmp", "tmpfile"+str(i)))
