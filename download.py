# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 11:58:29 2013

@author: elias
"""

import time, os.path
import medeley_fetch
import regex

ids = medeley_fetch.get_ids_for_keyword('ph')
ids.extend(medeley_fetch.get_ids_for_keyword('redfield ratio'))

for id in ids:
    print id
    keyword_path = regex.path_normalize(id)
    path = 'Data/'+keyword_path+'.txt'
    path = medeley_fetch.fix_length(path)
    if os.path.exists(path):
        pass
    else:
        medeley_fetch.get_abstract_for_id(id)
        time.sleep(8)