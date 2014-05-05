# -*- coding: utf-8 -*-
"""
Created on Thu May  1 13:27:20 2014

@author: elias
"""

if __name__ == "__main__":
    # Read parse xml
    xml = ET.parse("NParses/101371journalpone0082070.xml")
    for sentence in xml.iter('sentence'):
        print sentence
        