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
        try:
            keyword, tf = line.strip().split(':')
            df = url_fetch.get_count_for_keyword(keyword)
            if df < 2:
                tfidfs[keyword] = "n/a"
            else:
                idf = math.log((float(MEDLINE_SIZE)) / (float(df), 2))
                tfidfs[keyword] = float(tf)*idf
        except:
            print "Failed to download count index for " + keyword + ", probably due to timeout."

with open('tfidfs.txt', 'w') as file:
    for key in tfidfs[:]:
        file.write(key + ":" + str(tfidfs[key]) + "\n")