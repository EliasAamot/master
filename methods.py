# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 18:12:23 2013

@author: elias
"""
from regex import *
import urllib2 as urllib
from Bio import Entrez

MAX_CAP = 25000

def get_count_for_keyword(keyword):
    """
    path = 'Data/'+keyword+'.txt'
    if " " in keyword:
        keyword = '+'.join(keyword.split())
    keyword = path_normalize(keyword)
    try: 
        with open(path, 'r') as file:
            xml = file.read()
            return find_count(xml)
    except IOError:
        """
    Entrez.email = "eliasaa@stud.ntnu.no"
    handle = Entrez.esearch(db="pubmed", retmax=MAX_CAP, term=keyword)
    record = Entrez.read(handle)
#        with open(path, 'w') as file:
#            file.write(record)
    return int(record["Count"])
        
def get_ids_for_keyword(keyword):
    """
    if " " in keyword:
        keyword = '+'.join(keyword.split())
    keyword = path_normalize(keyword)
    path = 'Data/'+keyword+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
            return find_ids(xml)
    except IOError:
        """
    Entrez.email = "eliasaa@stud.ntnu.no"
    handle = Entrez.esearch(db="pubmed", retmax=MAX_CAP, term=keyword)
    record = Entrez.read(handle)
#        with open(path, 'w') as file:
#            file.write(record)
    return record["IdList"]

def get_title_for_id(theid):
    path = 'Data/'+theid+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
            return find_headline(xml)
    except IOError:
        Entrez.email = "eliasaa@stud.ntnu.no"
        handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml")
        xml = handle.read()
        with open(path, 'w') as file:
            file.write(xml)
        return find_headline(xml)
        
def get_abstract_for_id(theid):
    path = 'Data/'+theid+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
            return find_abstract_texts(xml)
    except IOError:
        Entrez.email = "eliasaa@stud.ntnu.no"
        handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml")
        xml = handle.read()
        with open(path, 'w') as file:
            file.write(xml)
        return find_abstract_texts(xml)
    