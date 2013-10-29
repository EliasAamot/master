# -*- coding: utf-8 -*-
"""
Methods for gathering medline papers based keywords or ids.

@author: elias
"""
from regex import *
import urllib2 as urllib
from Bio import Entrez

MAXCAP = 250000
BASE_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MAXDATE = "2014/01/01"

def get_count_for_keyword(keyword):
    xml = None
    if " " in keyword:
        keyword = '+'.join(keyword.split())
    keyword = path_normalize(keyword)
    path = 'Data/'+keyword+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + keyword
        url = BASE_URL + "esearch.fcgi?db=pubmed&term="+keyword+"&retmax="+str(MAXCAP)+"&maxdate="+MAXDATE
        response = urllib.urlopen(url)
        xml = response.read()
        with open(path, 'w') as file:
            file.write(xml)
    return find_count(xml)
        
def get_ids_for_keyword(keyword):
    xml = None
    if " " in keyword:
        keyword = '+'.join(keyword.split())
    keyword = path_normalize(keyword)
    path = 'Data/'+keyword+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + keyword
        url = BASE_URL + "esearch.fcgi?db=pubmed&term="+keyword+"&retmax="+str(MAXCAP)+"&maxdate="+MAXDATE
        response = urllib.urlopen(url)
        xml = response.read()
        with open(path, 'w') as file:
            file.write(xml)
    return find_ids(xml)

def get_title_for_id(theid):
    path = 'Data/'+theid+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
            return find_headline(xml)
    except IOError:
        print "Downloading " + str(theid)
        Entrez.email = "eliasaa@stud.ntnu.no"
        handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml", maxdate=MAXDATE)
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
        print "Downloading " + str(theid)
        Entrez.email = "eliasaa@stud.ntnu.no"
        handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml", maxdate=MAXDATE)
        xml = handle.read()
        if has_any_content(xml):
            with open(path, 'w') as file:
                file.write(xml)
            return find_abstract_texts(xml)
        else:
            return None
    