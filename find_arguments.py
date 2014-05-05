# -*- coding: utf-8 -*-
"""
Script to find all the arguments for detected trigger words
"""
import os, subprocess
import xml.etree.ElementTree as ET

colour_map = {"Variable":"deeppink",
              "Thing":"crimson",
              "Change":"green3",
              "Increase":"salmon",
              "Decrease":"turquoise",
              "Correlate":"gray",
              "Cause":"gray",
              "And":"green",
              "Or":"green",
              "RefExp":"gray"}

def get_colour(start, end, anns):
    """
        Finds the colour of a node, baesd on its participation in an annotated sequence
    """
    colour = None
    for ann in anns:
        if int(start) >= int(ann[1]) and int(end) <= int(ann[2]):
            colour = colour_map[ann[0]]
            break
    return colour

if __name__=="__main__":
    letsfind = ['increase', 'more', 'stimulate']    
    
    files = ["NParses/" + filename for filename in os.listdir("NParses")]
    
    for filen in files:
        xml = ET.parse(filen)
        # Read in corresponding annotation
        core_filename = filen[filen.index('/')+1:filen.index('.')]
        anns = [ann.strip().split()[1:4] for ann in open("ANN/"+core_filename+".ann") if ann.strip().split()[0][0] == "T"]
        for i, sentence in enumerate(xml.iter("sentence")):
            interesting = False
            for word in sentence.iter("lemma"):
                if word.text in letsfind:
                    interesting = True
            # If sentence is interesting, we want to graph it and stuff
            if interesting:
                dotstring = "digraph {\n"
                # Store nodes and colors
                for token in sentence.iter("token"):
                    _id = token.attrib['id']
                    _word = token.find('word').text
                    _startoffset = token.find('CharacterOffsetBegin').text
                    _endoffset = token.find('CharacterOffsetEnd').text
                    colour = get_colour(_startoffset, _endoffset, anns)
                    # Add the possibly coloured node to the graph specification
                    if colour:
                        dotstring += _word+_id+" [style = filled, fillcolor = "+colour+"];\n"
                    else:
                        dotstring += _word+_id+";\n"
                # Build actual graph content
                # iterate over the collapsed, ccprocessed dependences
                for dependency in sentence.iter('dependencies'):
                    if not dependency.attrib['type'] == "collapsed-ccprocessed-dependencies":
                        continue
                    for dep in dependency.iter('dep'):
                        _type = dep.attrib['type']
                        gov_node = dep.find('governor')
                        _gid = gov_node.attrib['idx']
                        _gword = gov_node.text
                        dep_node = dep.find('dependent')
                        _did = dep_node.attrib['idx']
                        _dword = dep_node.text
                        
                        dotstring += _gword+_gid+" -> "+_dword+_did+"[label="+_type+"];\n"
                dotstring += "}"
            
                with open("DepTrees/"+core_filename+"s"+str(i)+".dot", 'w') as dotfile:
                    dotfile.write(dotstring)
            
    # Convert dot to png FTW
    os.chdir("DepTrees")
    dotfiles = [f for f in os.listdir(os.getcwd()) if ".dot" in f]
    for dotfile in dotfiles:  
        args = ["dot", "-Tsvg", dotfile, "-o", dotfile[:dotfile.index('.')]+".svg"]
        subprocess.call(["dot", "-Tsvg", dotfile, "-o", dotfile[:dotfile.index('.'):]+".svg"])
    """
        text = open(filen, 'r').read()
        xml = json.loads(text)
#        print xml['gram']['sentences'][0].keys()

        # Convert all dependency texts to lower case
        dependencies = [[strr.lower() for strr in dep] for dep in xml['gram']['sentences'][0]['dependencies']]
        
        
        for dep in dependencies:
            if dep[1] in letsfind:
                findings[dep[1]].append(dep)
       
    for k, v in findings.items():        
        print k
        args = collections.defaultdict(set)
        for dep in v:
            args[dep[0]].add(dep[2])
        for kk, vv in args.items():
            print "\t"+kk
            for vvv in vv:
                print "\t\t"+vvv
                """