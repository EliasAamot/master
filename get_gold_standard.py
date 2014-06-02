# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:53:28 2014

@author: elias
"""
import regex
import json

YEAR = 2009
KEYWORD = "biological pump"

if __name__=="__main__":
    # Find the IDs of all papers with given KEYWORD
    keypath = regex.path_normalize(KEYWORD)
    path = 'IDs/'+ keypath + ".ids"
    try: 
        with open(path, 'r') as idfile:
            ids = [line.strip() for line in idfile]
    except IOError:
        print "File isn't downloaded!"
        exit()
        
    # Split into two parts, according to YEAR
    before = []
    after = []
    for iid in ids:
        path = "Data/"+iid+".txt"
        try:
            with open(path, 'r') as pfile:
                text = pfile.read()
                xml = json.loads(text)
                if int(xml['year']) > YEAR:
                    after.append(iid)
                else: 
                    before.append(iid)
        except IOError:
            print "File with ID", iid, "does not exist!"
            exit()
            
    print len(before)
    print len(after)
    
    # Find all NPs in the after and before sets
    after_nps = set()
    for iid in after:
        with open("NPs/"+iid+".xml", 'r') as npfile:
            for line in npfile:
                np, count = line.strip().split("\t")
                after_nps.add(np)
                
    before_nps = set()
    for iid in before:
        with open("NPs/"+iid+".xml", 'r') as npfile:
            for line in npfile:
                np, count = line.strip().split("\t")
                before_nps.add(np)
    
    print len(after_nps)
    print len(before_nps)
    print len(after_nps.difference(before_nps))