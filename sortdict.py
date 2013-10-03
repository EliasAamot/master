# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:37:32 2013

@author: elias
"""
from collections import defaultdict
from operator import itemgetter

class SortDict():
    
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
        tuples = sorted(tuples, key=itemgetter(1))[start:stop]
        return [key for key, value in tuples]
        
    def iterkeys(self):
        return self.dict.iterkeys()