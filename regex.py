# -*- coding: utf-8 -*-
"""
Methods for regular expression manipulation of strings.

@author: Elias
"""
import re

def has_any_content(xml):
    pattern = re.compile("(<PubmedArticleSet>)(.*?)(</PubmedArticleSet>)", re.DOTALL)
    match = pattern.search(xml)
    return match.group(2).strip() != ""

def find_count(xml):
    match = re.search("(<Count>)(.*?)(</Count>)", xml)
    if match == None:
        return 0
    else:
        return int(match.group(2))

def find_headline(xml):
    match = re.search("(<ArticleTitle>)(.*?)(</ArticleTitle>)", xml)        
    if match == None: return ""
    else: return match.group(2)
    
def find_ids(xml):
    matches = re.finditer("(<Id>)(.*?)(</Id>)", xml)
    return [match.group(2) for match in matches]
    
def find_abstract_texts(xml):
    matches = re.finditer("(<AbstractText)(.*?)(>)(.*?)(</AbstractText>)", xml)
    return [match.group(4) for match in matches]
    
def normalize(word):
    word = word.lower()
    word = re.sub("[^a-z ]", "", word)
    return word
    
def path_normalize(word):
    word = '+'.join(word.split())
    word = word.lower()
    word = re.sub("[^a-z+]", "", word)
    return word
    
def np_normalize(np):
    np = np.lower().strip()
    np = re.sub("[^ 0-9\-a-z+]", "", np)
    np = re.sub(" [ ]+", " ", np)
    np= np.strip()
    return np