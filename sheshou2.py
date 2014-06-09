# -*- coding: utf-8 -*-
"""
An Arrowsmith-like LBKD system utilizing the Stanford Core NLP Toolkit and the Medeley database.

@author: elias
"""
import medeley_fetch, sortdict, extract_nps
import os, codecs, random
from collections import defaultdict

YEAR = 2009

def query(keyword):
    print "Selecting papers containing the A-keywords..."
    ids = fetch_paper_ids(keyword)
    print "Fetching NPs from papers..."
    npc = get_nps_from_papers(ids)
    print "Mining for association rules in L(a)..."
    B = mine_association_rules(npc)
    print "Extracting C from L(B)..."
    C = sortdict.SortDict()
    for b in B:
        bids = fetch_paper_ids(b)
        if not len(bids):
            continue
        bnpc = get_nps_from_papers(bids)
        C_j = mine_association_rules(bnpc)
        for c in C_j:
            C[c] += 1
    print " Results:"
    for key in C[:10]:
        print key, ":", C[key]

def fetch_paper_ids(keyword):
    f = medeley_fetch.Fetcher()
    ids = f.get_ids_for_keyword(keyword)
    
    id_sample = []
    while len(id_sample) < 100 and len(ids):
        check = random.choice(ids)
        ids.remove(check)
        year = f.get_year_for_id(check)
        
        if year <= YEAR:
            id_sample.append(check)
            
    return id_sample
    
    
def get_nps_from_papers(ids):
    npps = []
        
    for iid in ids:
        if not os.path.exists(os.path.join("NPs", iid+".xml")):
            extract_nps.extract_nps_single_paper(iid)
            
        with codecs.open(os.path.join("NPs", str(iid)+".xml"), mode='r', encoding='utf-8') as npfile:
            nps = dict([line.strip().split("\t") for line in npfile])

        npps.append(nps)
    return npps
    
def mine_association_rules(npc):
    # Association Rule Collection is a map from itemset to support count
    support = defaultdict(int)
    confidence = defaultdict(int)
    
    # Calculate the support for every NP, and remove those with less than average support
    for paper in npc:
        for np, count in paper.iteritems():
            support[np] += 1

    avg_support = float(sum(support.values()))/float(len(support.values()))

    supported = [np for np, suprt in support.iteritems() if suprt >= avg_support]
    
    # Calculate the confidence for every supported NP
    f = medeley_fetch.Fetcher()
    for np in supported:
        try:
            confidence[np] = float(support[np]) / float(f.get_count_for_keyword(np))
        except ZeroDivisionError:
            # Can happen with some keywords that you cannot search with, such
            # as /
            continue
        
    avg_confidence = float(sum(confidence.values()))/float(len(confidence.values()))

    accepted = [np for np, conf in confidence.iteritems() if conf >= avg_confidence]
    
    """ # For Logging
    with codecs.open('stats.txt', mode='w', encoding='utf-8') as fil:
        fil.write("Average support: "+str(avg_support)+"\n")
        fil.write("Average confidence: "+str(avg_confidence)+"\n")
        fil.write("All NPs: " + str(len(support))+"\n")
        fil.write("Supported: " + str(len(supported))+"\n")
        fil.write("Confidence: " + str(len(confidence))+"\n")
        fil.write("Accepted: " +str(len(accepted))+"\n")
        for np, supportt in support.iteritems():
            text = np + "\t" + str(supportt)
            if np in confidence:
                text += "\t" + str(confidence[np])
            else:
                text += "\t" + "N/A"
            if np in accepted:
                text += "\t" + "Yes"
            else:
                text += "\t" + "No"
            fil.write(text+"\n")
    """
            
    return accepted
    
if __name__=="__main__":
    query("biological pump")