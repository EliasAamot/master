# -*- coding: utf-8 -*-
"""
Methods for gathering medline papers based keywords or ids.

@author: elias
"""
from regex import *
import urllib, urllib2, json
import datetime

SEARCH_BASE_URL = "https://api-oauth2.mendeley.com/oapi/documents/search/"
DETAIL_BASE_URL = "https://api-oauth2.mendeley.com/oapi/documents/details/"

MAX_PATH_LENGTH = 255
FOLDER_NAME_LENGTH = 5 # len("Data/")

def get_auth_string(access_token):
    return "/?access_token=" + access_token

def fix_length(path):
    """
        Sometimes the path produced for a keyword can become too long for the OS to handle, especially in the cases where the keyword is a complex NP. To handle these situations, I assume that the last 255 characters (including '.txt') is a sufficiently unique indicator of the keyword, even if this might not be the case.
    """
    if len(path) > MAX_PATH_LENGTH+FOLDER_NAME_LENGTH:
        folder, post_folder_path = path.split("/")
        post_folder_path = post_folder_path[-MAX_PATH_LENGTH:]
        path = folder+"/"+post_folder_path
    return path
    

def get_count_for_keyword(keyword, access_token):
    keyword_path = path_normalize(keyword)
    path = 'Counts/'+keyword_path+'.cnt'
    path = fix_length(path)
    try: 
        with open(path, 'r') as file:
            count = int(file.read().strip())
    except IOError:
        print "Downloading " + keyword
        done = False
        while not done:
            try:
                search_query = urllib2.quote("title:"+keyword) 
                url = SEARCH_BASE_URL + search_query + get_auth_string(access_token)
                print url
                xml_dict = json.loads(urllib2.urlopen(url).read())
                count = xml_dict['total_results']
                if count == None:
                    return 0
                count = int(count)
                done = True
            except Exception as e:
                if '429' in str(e):
                    print "HTTP Error 429: Too many requests. Try again in one hour or more."
                    return None
                else:
                    print "Exception " + str(e) + " occured while downloading paper " + keyword + ". Trying again."
        with open(path, 'w') as file:
            file.write(str(count) + "\n")
    return count
        
def get_ids_for_keyword(keyword, access_token):
    keyword_path = path_normalize(keyword)
    path = 'IDs/'+keyword_path+'.ids'
    path = fix_length(path)
    try: 
        with open(path, 'r') as file:
            ids = [line.strip() for line in file]
    except IOError:
        print "Downloading " + keyword
        ids = []
        done = False
        current_page = 0
        while not done:
            try:
                search_query = urllib2.quote('"'+keyword+'"') 
                url = SEARCH_BASE_URL + search_query + get_auth_string(access_token) + "&page=" + str(current_page) + "&items=100"
                xml_dict = json.loads(urllib2.urlopen(url).read())
                ids.extend([document['uuid'] for document in xml_dict['documents']])                
                current_page += 1
                print str(current_page) + "/" + str(xml_dict['total_pages'])
                if current_page > int(xml_dict['total_pages']):
                    done = True
            except Exception as e:
                if '429' in str(e):
                    print "HTTP Error 429: Too many requests. Try again in one hour or more."
                    return None
                else:
                    print "Exception " + str(e) + " occured while downloading paper " + keyword + ". Trying again."
        with open(path, 'w') as file:
            for id in ids:
                file.write(id + "\n")
    return ids

def get_abstract_for_id(theid, access_token):
    path = 'Data/'+theid+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + str(theid)
        fetched = False
        while not fetched:
            try:
                search_query = theid
                url = DETAIL_BASE_URL + search_query + get_auth_string(access_token)
                xml = urllib2.urlopen(url).read()
                time.sleep(8)
                fetched = True
            except Exception as e:
                if '429' in str(e):
                    print "HTTP Error 429: Too many requests. Try again in one hour or more."
                    raise Exception('TooManyRequestsException')
                else:
                    print "Unknown exception " + str(e) + " occured while downloading paper " + theid + ". Trying again."
    with open(path, 'w') as file:
        file.write(xml)
    xml_dict = json.loads(xml)
    try:
        if 'abstract' in xml_dict.keys():
            return xml_dict['abstract']
        else:
	    pass
            #raise Exception('PaperHasNoAbstractException')
    except AttributeError:
        print xml_dict

import time

class Fetcher:
    """
        An object is used for convenience to keep track of authentication,
        and time whether a new access token is required. 
    """
    def __init__(self):
        self.access_token = None
        self.access_expires = time.time()-1
        
    def get_access_token(self):
        if time.time() > self.access_expires:
            self._get_new_access_token()
        return self.access_token
        
    def get_long_access_token(self):
        # Use this to force the access token to be valid for at least 10 minutes
        if time.time() + 600000 > self.access_expires:
            self._get_new_access_token()
        return self.access_token

    def _get_new_access_token(self):
        url = 'https://api-oauth2.mendeley.com/oauth/token'
        values = {'client_id' : '143',
                  'client_secret' : 'J6s8!!VYae{0$lD2',
                  'grant_type':'client_credentials', }
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        xml = json.loads(response.read())
        
        self.access_token = xml['access_token']
        self.access_expires = time.time() + (int(xml['expires_in'])) - 5    
        # -5000 to ensure that the token does not expire even counting some delay
        
    def get_abstracts_for_id(self, theid):
        return get_abstract_for_id(theid, self.get_access_token())
        
    def get_ids_for_keyword(self, keyword):
        return get_ids_for_keyword(keyword, self.get_long_access_token())
        
    def get_count_for_keyword(self, keyword):
        return get_count_for_keyword(keyword, self.get_access_token())
                

if __name__=="__main__":
    pass
