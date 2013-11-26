# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 16:06:46 2013

@author: elias
"""
import os, collections
import medeley_fetch

def find_and_print(keywords):
    index_dictionary = collections.defaultdict(set)
    
    for dirpath, dirnames, filenames in os.walk("NPs"):
        for filename in filenames:
            with open(os.path.join("NPs", filename), 'r') as file:
                for line in file:
                    split = line.strip().split("\t")
                    for keyword in keywords:
                        if keyword in split:
                            index_dictionary[keyword].add(filename[:filename.index(".")])
    
    return set.intersection(*index_dictionary.values())

if __name__=="__main__":
    keywords = ["ocean acidification", "calcification"]
    
    ids = find_and_print(keywords)

    for id in ids:
        print medeley_fetch.get_abstract_for_id(id)
        print "\n"