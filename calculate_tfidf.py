# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 10:32:58 2013

@author: elias
"""
import url_fetch, math, sortdict

MEDLINE_SIZE = 23000000
tfidfs = sortdict.SortDict()

with open('results.txt', 'r') as file:
    for line in file:
        try:
            keyword, tf = line.strip().split(':')
            df = url_fetch.get_count_for_keyword(keyword)
            if df < 2:
                tfidfs[keyword] = 0.0
            else:
                idf = math.log(float(MEDLINE_SIZE) / float(df), 2)
                tfidfs[keyword] = float(tf)*idf
        except Exception as e:
            print "Exception " + str(e) + " occurred. Skipping the keyword " + keyword + "."

with open('tfidfs.txt', 'w') as file:
    for key in tfidfs[:]:
        file.write(key + ":" + str(tfidfs[key]) + "\n")