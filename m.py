# -*- coding: utf-8 -*-
"""
Created on Mon Mar 17 10:21:51 2014

@author: elias
"""
import re

filepath = "/home/elias/.tees/corpora/DDI11-train.xml"

with open(filepath, 'r') as file:
    text = file.read()

pattern = re.compile(r'<analyses>(.*?)</analyses>', flags=re.DOTALL)
text = pattern.sub("", text)

with open(filepath+"nonlp", 'w') as file:
    file.write(text)