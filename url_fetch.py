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
MAX_PATH_LENGTH = 255
FOLDER_NAME_LENGTH = 5 # len("Data/")

def fix_length(path):
    """
        Sometimes the path produced for a keyword can become too long for the OS to handle, especially in the cases where the keyword is a complex NP. To handle these situations, I assume that the last 255 characters (including '.txt') is a sufficiently unique indicator of the keyword, even if this might not be the case.
    """
    if len(path) > MAX_PATH_LENGTH+FOLDER_NAME_LENGTH:
        folder, post_folder_path = path.split("/")
        post_folder_path = post_folder_path[-MAX_PATH_LENGTH:]
        path = folder+"/"+post_folder_path
    return path
    

def get_count_for_keyword(keyword):
    xml = None
    if " " in keyword:
        keyword = '+'.join(keyword.split())
    keyword = path_normalize(keyword)
    path = 'Data/'+keyword+'.txt'
    path = fix_length(path)
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + keyword
        fetched = False
        while not fetched:
            try:
                url = BASE_URL + "esearch.fcgi?db=pubmed&term="+keyword+"&retmax="+str(MAXCAP)+"&maxdate="+MAXDATE
                fetched = True
            except Exception as e:
                print "Exception " + str(e) + " occured while downloading paper " + keyword + ". Trying again."
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
    path = fix_length(path)
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + keyword
        fetched = False
        while not fetched:
            try:
                url = BASE_URL + "esearch.fcgi?db=pubmed&term="+keyword+"&retmax="+str(MAXCAP)+"&maxdate="+MAXDATE
                fetched = True
            except Exception as e:
                print "Exception " + str(e) + " occured while downloading paper " + keyword + ". Trying again."
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
        fetched = False
        while not fetched:
            try:
                handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml", maxdate=MAXDATE)
                fetched = True
            except Exception as e:
                print "Exception " + str(e) + " occured while downloading paper " + theid + ". Trying again."
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
        fetched = False
        while not fetched:
            try:
                handle = Entrez.efetch(db="pubmed", id=theid, retmode="xml", maxdate=MAXDATE)
                fetched = True
            except Exception as e:
                print "Exception " + str(e) + " occured while downloading paper " + theid + ". Trying again."
        xml = handle.read()
        if has_any_content(xml):
            with open(path, 'w') as file:
                file.write(xml)
            return find_abstract_texts(xml)
        else:
            return None
    