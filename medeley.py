# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:20:46 2013

@author: elias
"""

#import urllib2, urllib
#import json
import medeley_fetch

for id in medeley_fetch.get_ids_for_keyword("ocean acidification"):
    medeley_fetch.get_abstract_for_id(id)

print medeley_fetch.get_abstract_for_id("b61399bb-049d-30c9-93d8-62bd3731bb2e")
"""
CONSUMER_KEY = "939b208ebeea32b816da61a1bce7de4605278cbae"
AUTH = "/?consumer_key=" + CONSUMER_KEY
SEARCH_BASE_URL = "http://api.mendeley.com/oapi/documents/search/"
DETAIL_BASE_URL = "http://api.mendeley.com/oapi/documents/details/"
terms = 'title:"Ocean acidification"'

url = SEARCH_BASE_URL + urllib.quote(terms) + AUTH + "&page=1"
print url

response = urllib2.urlopen(url)
xml = response.read()
xml_dict = json.loads(xml)

documents = xml_dict['documents']
uuids = [document['uuid'] for document in documents]

print xml_dict

for uuid in uuids:
    print uuid
    """
"""
    url = DETAIL_BASE_URL + uuid + AUTH
    response = urllib2.urlopen(url)
    xml = response.read()
    xml_dict = json.loads(xml)
    print xml_dict['abstract']
   """