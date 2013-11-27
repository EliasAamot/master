# -*- coding: utf-8 -*-
"""
Methods for gathering medline papers based keywords or ids.

@author: elias
"""
from regex import *
import urllib2, json
import nlp

CONSUMER_KEY = "939b208ebeea32b816da61a1bce7de4605278cbae"
AUTH = "/?consumer_key=" + CONSUMER_KEY

SEARCH_BASE_URL = "http://api.mendeley.com/oapi/documents/search/"
DETAIL_BASE_URL = "http://api.mendeley.com/oapi/documents/details/"

BASE_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MAX_PATH_LENGTH = 255
FOLDER_NAME_LENGTH = 5 # len("Data/")

def fix_length(path):
    """
        Sometimes the path produced for a keyword can become too long for the OS to handle, especially in the cases where the keyword is a complex NP. To handle these situations, I assume that the last 255 characters (including '.txt') is a sufficiently unique indicator of the keyword, even if this might not be the case.
    """
    if len(path) > MAX_PATH_LENGTH+FOLDER_NAME_LENGTH:
        folder, post_folder_path = path.split("/")
        post_folder_path = post_folder_path[-MAX_PATH_LENGTH:]
        path = folder+"/"+post_folder_path
    return path
    

def get_count_for_keyword(keyword):
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
                url = SEARCH_BASE_URL + search_query + AUTH
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
        
def get_ids_for_keyword(keyword):
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
                url = SEARCH_BASE_URL + search_query + AUTH + "&page=" + str(current_page) + "&items=100"
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

def get_abstract_for_id(theid):
    path = 'Papers/'+theid+'.txt'
    try: 
        with open(path, 'r') as file:
            xml = file.read()
    except IOError:
        print "Downloading " + str(theid)
        fetched = False
        while not fetched:
            try:
                search_query = theid
                url = DETAIL_BASE_URL + search_query + AUTH
                xml = urllib2.urlopen(url).read()
                fetched = True
            except Exception as e:
                if '429' in str(e):
                    print "HTTP Error 429: Too many requests. Try again in one hour or more."
                    return None
                else:
                    print "Exception " + str(e) + " occured while downloading paper " + theid + ". Trying again."
    with open(path, 'w') as file:
        file.write(xml)
    xml_dict = json.loads(xml)
    try:
        if 'abstract' in xml_dict.keys():
            return xml_dict['abstract']
        else:
            return None
    except AttributeError:
        print xml_dict

if __name__=="__main__":
    pass
    