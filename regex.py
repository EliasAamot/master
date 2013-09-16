# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 14:09:48 2013

@author: Elias
"""
import re

def find_count(xml):
    match = re.search("(<Count>)(.*?)(</Count>)", xml)
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
    word = re.sub("[^a-z]", "", word)
    return word
    
def path_normalize(word):
    word = word.lower()
    word = re.sub("[^a-z+]", "", word)
    return word