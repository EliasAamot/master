# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 15:45:10 2013

@author: elias
"""
stop_list = ['raynaud', 'rp']
chosen = 0

with open('tfidfs.txt', 'r') as file:
    for line in file:
        keyword, score = line.strip().split(':')
        stop_it = False
        for stop_word in stop_list:
            if stop_word in keyword:
                stop_it = True
        
        if not stop_it:
            print keyword
            chosen += 1
        if chosen >= 50:
            break
            