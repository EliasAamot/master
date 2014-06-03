# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:53:28 2014

@author: elias
"""
import regex, codecs
import json, os
import medeley_fetch
import extract_nps

YEAR = 2009
KEYWORD = "biological pump"


if __name__=="__main__":
    f = medeley_fetch.Fetcher()
    ids = f.get_ids_for_keyword(KEYWORD)
        
    # Split into two parts, according to YEAR
    before = []
    after = []
    for iid in ids:
        year = f.get_year_for_id(iid)
        if year > YEAR:
            after.append(iid)
        else:
            before.append(iid)
            
    print len(before)
    print len(after)
    
    # Find all NPs in the after and before sets
    after_nps = set()
    for iid in after:
        print iid
        if not os.path.exists("NPs/"+iid+".xml"):
            extract_nps.extract_nps_single_paper(iid)
        
        npfile = open("NPs/"+iid+".xml", 'r')
        for line in npfile:
            np, count = line.strip().split("\t")
            after_nps.add(np)
             
             
    before_nps = set()
    for iid in before:
        print iid
        if not os.path.exists("NPs/"+iid+".xml"):
            extract_nps.extract_nps_single_paper(iid)
        
        npfile = open("NPs/"+iid+".xml", 'r')
        for line in npfile:
            np, count = line.strip().split("\t")
            before_nps.add(np)
    
    with codecs.open("tmp/after.nps", mode='w', encoding='utf-8') as fil:
        for np in after_nps:
            fil.write(unicode(np + "\n", 'utf-8'))
            
    with codecs.open("tmp/before.nps", mode='w', encoding='utf-8') as fil:
        for np in before_nps:
            fil.write(unicode(np + "\n", 'utf-8'))
            
    with codecs.open("tmp/diff.nps", mode='w', encoding='utf-8') as fil:
        for np in after_nps.difference(before_nps):
            fil.write(unicode(np + "\n", 'utf-8'))
            
    with codecs.open("tmp/inter.nps", mode='w', encoding='utf-8') as fil:
        for np in after_nps.intersection(before_nps):
            fil.write(unicode(np + "\n", 'utf-8'))