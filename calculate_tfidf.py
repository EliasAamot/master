# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 10:32:58 2013

@author: elias
"""
import url_fetch, math, sortdict

MEDLINE_SIZE = 2300000
tfidfs = sortdict.SortDict()

with open('results.txt', 'r') as file:
    for line in file:
        keyword, tf = line.strip().split(':')
        df = url_fetch.get_count_for_keyword(keyword)
        idf = math.log((float(MEDLINE_SIZE)+1) / (float(df)+1), 2)
        tfidfs[keyword] = float(tf)*idf

with open('tfidfs.txt', 'w') as file:
    for key in tfidfs[:]:
        file.write(key + ":" + tfidfs[key] + "\n")