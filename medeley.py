# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:20:46 2013

@author: elias
"""

import urllib2, urllib
import json

CONSUMER_KEY = "939b208ebeea32b816da61a1bce7de4605278cbae"
AUTH = "/?consumer_key=" + CONSUMER_KEY
SEARCH_BASE_URL = "http://api.mendeley.com/oapi/documents/search/"
DETAIL_BASE_URL = "http://api.mendeley.com/oapi/documents/details/"
terms = 'title:"Ocean acidification"'

url = SEARCH_BASE_URL + urllib.quote(terms) + AUTH + "&items=499"
print url

response = urllib2.urlopen(url)
xml = response.read()
xml_dict = json.loads(xml)

documents = xml_dict['documents']
uuids = [document['uuid'] for document in documents]

for uuid in uuids:
    print uuid
    """
    url = DETAIL_BASE_URL + uuid + AUTH
    response = urllib2.urlopen(url)
    xml = response.read()
    xml_dict = json.loads(xml)
    print xml_dict['abstract']
    """