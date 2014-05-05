# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 10:12:17 2014

@author: elias
"""
import httplib2
import re

def get_fetch_url(id):
    return 'http://www.plosone.org/article/fetchObject.action?uri=info:doi/{0}&representation=XML'.format(id)
def get_api_url(query):
    return 'http://api.plos.org/search?q="{0}"&api_key=3pezRBRXdyzYW6ztfwft'.format('+'.join(query.split()).strip('+'))

q = "ocean acidification"
url = get_api_url(q)

h = httplib2.Http()
(resp_headers, content) = h.request(url, "GET")

for i, match in enumerate(re.finditer(r'<str name="id">(.*?)</str>', content)):
    id = match.group(1)
    resp_header, xml = h.request(get_fetch_url(id), "GET")
    with open("PLOS/"+str(i)+".xml", 'w') as file:
        file.write(xml)
