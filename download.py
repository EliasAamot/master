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
ids.extend(medeley_fetch.get_ids_for_keyword('co2'))
ids.extend(medeley_fetch.get_ids_for_keyword('carbon dioxide'))
ids.extend(medeley_fetch.get_ids_for_keyword('ocean acidification'))
ids.extend(medeley_fetch.get_ids_for_keyword('global warming'))
ids.extend(medeley_fetch.get_ids_for_keyword('phytoplankton'))
ids.extend(medeley_fetch.get_ids_for_keyword('krill'))
ids.extend(medeley_fetch.get_ids_for_keyword('fish'))
ids.extend(medeley_fetch.get_ids_for_keyword('fishing'))
ids.extend(medeley_fetch.get_ids_for_keyword('iron enrichment'))
ids.extend(medeley_fetch.get_ids_for_keyword('antarctic'))
ids.extend(medeley_fetch.get_ids_for_keyword('arctic'))
ids.extend(medeley_fetch.get_ids_for_keyword('patagonia'))
ids.extend(medeley_fetch.get_ids_for_keyword('biological pump'))
ids.extend(medeley_fetch.get_ids_for_keyword('primary production'))
ids.extend(medeley_fetch.get_ids_for_keyword('ocean'))
ids.extend(medeley_fetch.get_ids_for_keyword('oceanic'))

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
