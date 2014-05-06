# -*- coding: utf-8 -*-
"""
Scripts that extracts all triggers for a given type from Brat ann files
"""
import os, collections

if __name__ == "__main__":
    
    brat_folder = "ANN"
    filenames = [brat_folder + "/" + filn for filn in os.listdir(brat_folder) if ".ann" in filn]
    
    triggers = collections.defaultdict(list)  
    
    for filename in filenames:
        file = open(filename, 'r')
        for line in file:
            line = line.strip().split()
            
            # Ignore anything but triggers
            if not "T" in line[0]:
                continue
            
            trigger_text = ' '.join(line[4:]).strip().lower()            
            triggers[line[1]].append(trigger_text)
    
    # Count and present nicely
    for t in triggers:
        tStr = t + "\n"
        
        counts = collections.defaultdict(int)
        for tt in triggers[t]:
            counts[tt] += 1
            
        for key, value in counts.iteritems():
            tStr += "\t"+key+":"+str(value)+"\n"
            
        print tStr