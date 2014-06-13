# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 15:37:32 2013

@author: elias
"""
from collections import defaultdict
from operator import itemgetter

class SortDict():
    """
        SortDict is a wrapper class for dict which contains methods that can be useful when using a dict to count things, and collect the results in order sorted by the number of occurrences.
        
        The most useful improvement over standard python dicts is the __getslice__ function.
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
        """
            Extracts the (start, stop) most common keys, sorted by the number of counts.
        """
        tuples = [(key, self.dict[key])for key in self.dict.iterkeys()]
        tuples = sorted(tuples, key=itemgetter(1), reverse=True)[start:stop]
        return [key for key, value in tuples]  
    
    def iteritems(self):
        return self.dict.iteritems()
    
    def iterkeys(self):
        return self.dict.iterkeys()
    
    def keys(self):
        return self.dict.keys()
        
    def itervalues(self):
        return self.dict.itervalues()
    
    def values(self):
        return self.dict.values()
        
    def join(self, other_dict):
        for key in other_dict.keys():
            self.dict[key] += int(other_dict[key])
            
    def __len__(self):
        return len(self.dict)