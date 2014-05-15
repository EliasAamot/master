# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 11:58:29 2013

@author: elias
"""

import time, os.path
import medeley_fetch
import regex

fetcher = medeley_fetch.Fetcher()

ids = fetcher.get_ids_for_keyword('primary production')

for id in ids:
    print id
    keyword_path = regex.path_normalize(id)
    path = 'Data/'+keyword_path+'.txt'
    path = medeley_fetch.fix_length(path)
    if os.path.exists(path):
        pass
    else:
        fetcher.get_abstract_for_id(id)
