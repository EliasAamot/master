# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:37:32 2013

@author: elias
"""
from collections import defaultdict
from operator import itemgetter

class SortDict():
    """
        A class for doing stuff.
    """
    
    def __init__(self):
        self.dict = defaultdict(int)
    
    def __setitem__(self, key, value):
        self.dict[key] = value
        
    def __getitem__(self, key):
        return self.dict[key]
    
    def __contains__(self, key):
        return key in self.dict
        
    def __getslice__(self, start, stop):
        tuples = [(key, self.dict[key])for key in self.dict.iterkeys()]
        tuples = sorted(tuples, key=itemgetter(1), reverse=True)[start:stop]
        return [key for key, value in tuples]

    def get_sorted(self, get_values=False):
        start = 0; stop = len(self.dict.keys())
        tuples = [(key, self.dict[key])for key in self.dict.iterkeys()]
        tuples = sorted(tuples, key=itemgetter(1), reverse=True)[start:stop]
        if get_values:
            return tuples
        else:
            return [key for key, value in tuples]        
        
    def iterkeys(self):
        return self.dict.iterkeys()