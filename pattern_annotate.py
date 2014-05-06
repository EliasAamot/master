# -*- coding: utf-8 -*-
"""
Script that automatically annotates papers according to the patterns given.

"""
import os, collections, subprocess
import xml.etree.ElementTree as ET

#
# Constants
#

target_folder = "DevPapers"

pattern_folder = "patterns"
increase_pattern_file = "increase.ptns"
decrease_pattern_file = "decrease.ptns"
change_pattern_file = "change.ptns"

coreNLPpath = os.path.join(os.getcwd(), "sfcnlp")


#
# Data structures
#

class Pattern:
    def __init__(self, change_type, is_thing):
        self.change_type = change_type
        self.is_thing = is_thing
        self.subpatterns = list()
    def __repr__(self):
        thingstring = "variable"
        if self.is_thing: thingstring = "thing"
        return "Pattern_"+self.change_type+"_"+thingstring+"_"+str(self.subpatterns)

class Node:
    def __init__(self, id, lemma):
        self.id = id
        self.lemma = lemma
        self.inedges = []
        self.outedges = []
    def __repr__(self):
        return str(self.id) + ":" + self.lemma
        
class Edge:
    def __init__(self, to_id, from_id, dep):
        self.to_id = to_id
        self.from_id = from_id
        self.dep = dep

#
# Main subroutines
#

def load_patterns():
    """
        Method to read in the pattern files, and also partially verify the 
        correctness of them.
    """
    # Initialize an empty pattern database
    patterns = collections.defaultdict(list)
    # Current trigger is used during pattern reading
    current_trigger = None
    
    # Pack up the filenames with the type patterns stored in there
    types_and_files = [("increase", os.path.join(pattern_folder, increase_pattern_file)),
                       ("decrease", os.path.join(pattern_folder, decrease_pattern_file)),
                       ("change", os.path.join(pattern_folder, change_pattern_file)) ]
    
    # Read in the patterns
    for change_type, filename in types_and_files:
        with open(filename, 'r') as filee:
            for line in filee:
                split = line.strip().split()
                # Skip comments and empty lines
                if not len(split): continue
                if split[0][0] == '#': continue
                
                # If the current line is a TRIGGER line, update which trigger we are working with
                if split[0].upper() == 'TRIGGER':
                    # Some minor syntax checking of trigger script
                    assert len(split) == 2, "TRIGGER must consist of the 'TRIGGER' keyword and the trigger, and nothing else"
                    current_trigger = split[1]
                # If the current line is something else, it is a pattern for the given trigger
                else:
                    # Do some minor correctness checking of the trigger script
                    assert current_trigger, "A trigger must be specified before you can start writing patterns!"
                    assert split[0].upper() == 'VAR' or split[0].upper() == "THN", "Keyword " + split[0] + " not recognized!"
                    
                    # Build new pattern based on information given in script
                    new_pattern_is_thing = (split[0].upper() == "THN")
                    new_pattern_change_type = change_type
                    new_pattern = Pattern(new_pattern_change_type, new_pattern_is_thing)
                    
                    # Extract the subpatterns by splitting on semicolon
                    subpatterns_domain = split[1:]
                    subpatterns = []
                    while ';' in subpatterns_domain:
                        first_subpattern = subpatterns_domain[:subpatterns_domain.index(';')]
                        subpatterns.append(first_subpattern)
                        subpatterns_domain = subpatterns_domain[subpatterns_domain.index(';')+1:]
                    # Then add the final subpattern that is not split by any semicolons
                    subpatterns.append(subpatterns_domain)
                    
                    # Do some syntax checking of subpatterns;
                    # Check that there is only one T per subpattern, and only one N or S.
                    # Check that each element is either a string (""), a dependency, or X,T,N or S
                    for subpattern in subpatterns:
                        assert subpattern.count('T') <= 1, "Error in line " + line + ": There can only be one Trigger (T) per subpattern!"
                        assert subpattern.count('N')+subpattern.count('S') <= 1, "Error in line " + line + ": There can only be one N or S target per subpattern!"
                        for element in subpattern:
                            accept = False
                            # Element is string
                            if element[0] == '"' and element[-1] == '"':
                                accept = True
                            # Element is accepted variable
                            elif element in ['T', 'N', 'X', 'S']:
                                accept = True
                            # Element is a dependency
                            elif element in ['prep', 'pobj', 'amod', 'nsubj', 'nsubjpass', 
                                             'dobj', 'nn', 'vmod', 'iobj', 'advmod', 'dep',
                                             'xcomp', 'aux', 'ccomp', 'rcmod', 'pcomp',
                                             'appos', 'advcl', 'mark']:
                                accept = True
                            # Element is a negation
                            elif element == "!":
                                accept = True
                            assert accept, "Element '" + element + "' is not an accepted element type of a pattern!"
                    # Do some correctness checking of entire pattern
                    # Needs at least one T, and at least one N or S
                    t_count = 0; n_s_count = 0
                    for subpattern in subpatterns:
                        for element in subpattern:
                            if element == 'T':
                                t_count += 1
                            if element in ['N', 'S']:
                                n_s_count += 1
                    assert t_count > 0, "There needs to be at least one occurence of the trigger word in a pattern!"
                    assert n_s_count > 0, "There needs to be exactly one occurence of N or S in a pattern!"
                    
                    # Assuming that the entire pattern is accepted, add it to the pattern base
                    new_pattern.subpatterns = subpatterns
                    patterns[current_trigger].append(new_pattern)
        collections.defaultdict(list) 
    return patterns

def parse_papers():
    parsed_files = [filename[:filename.index('.')]+".txt" for filename in os.listdir(target_folder) if '.xml' in filename]
    filenames = [os.path.join(target_folder, filename) for filename in os.listdir(target_folder) if '.txt' in filename and not filename in parsed_files]
    
    if not filenames: return
    
    with open(os.path.join(target_folder,"filelist.tmp"), 'w') as tmpfile:
        for filename in filenames:
            tmpfile.write(filename + "\n")
    
    subprocess.call(["java", "-cp", 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1.jar") + ":" + 
          os.path.join(coreNLPpath, "stanford-corenlp-3.3.1-models.jar") + ":" + 
          os.path.join(coreNLPpath, "xom.jar") + ":" + 
          os.path.join(coreNLPpath, "joda-time.jar") + ":" + 
          os.path.join(coreNLPpath, "jollyday.jar") + ":" + 
          os.path.join(coreNLPpath, "ejml-0.23.jar"), 
          "-Xmx3g","edu.stanford.nlp.pipeline.StanfordCoreNLP",
          "-annotators", "tokenize,cleanxml,ssplit,pos,lcollections.defaultdict(list) emma,parse", "-ssplit.eolonly", "-newlineIsSentenceBreak"
          "-outputExtension", ".xml", "-replaceExtension", "-outputDirectory", target_folder, 
          "-filelist", os.path.join(target_folder, "filelist.tmp")])
          
    os.remove(os.path.join(target_folder,"filelist.tmp"))
          

def pattern_matching(pattern_base):
    """
        Perform pattern matching with provided pattern database
    """
    
    papers = [os.path.join(target_folder, paper) for paper in os.listdir(target_folder) if ".xml" in paper]
    
    for paper in papers:
        xml = ET.parse(paper)
        
        # For every sentence, build a graph and try pattern matching in the graph
        for sentence in xml.iter('sentence'):
            #            
            # Graph building            
            #
            
            # Indices for easy and quick access to ndoes, by lemma and by index
            lemma_to_nodes_idx = collections.defaultdict(list)        
            id_to_node_idx = {}       
            # Build the nodes in the graph from tokens, remember to include a root node
            root = Node("0", "ROOT")
            id_to_node_idx["0"] = root
            nodes = [root]
            for token in sentence.iter('token'):
                id = token.attrib['id']
                lemma = token.find('lemma').text
                node = Node(id, lemma)
                nodes.append(node)
                lemma_to_nodes_idx[lemma].append(node)
                id_to_node_idx[id] = node
            # Connect nodes by dependency edges
            edges = []
            for dependencies in sentence.iter('dependencies'):
                # Use only the basic dependencies. Ignore the collapsed ones
                if dependencies.attrib['type'] != "basic-dependencies":
                    continue
                # Build an edge for every dependency
                for dep in dependencies.iter('dep'):
                    dep_type = dep.attrib['type']
                    from_id = dep.find('governor').attrib['idx']
                    to_id = dep.find('dependent').attrib['idx']
                    edge = Edge(to_id, from_id, dep_type)
                    edges.append(edge)
                    id_to_node_idx[from_id].outedges.append(edge)
                    id_to_node_idx[to_id].inedges.append(edge)
            
            #
            # Pattern matching
            #
            
            # For each of the triggers, see if it is triggered by a lemma
            for trigger in pattern_base:
                if trigger in lemma_to_nodes_idx.keys():
                    # If there is a trigger match, try to match each of the 
                    # patterns of that trigger until one matches, or they all fail.
                    for pattern in pattern_base[trigger]:
                        print pattern
        
    

if __name__ == "__main__":
    print "Loading in and verifying patterns..."
    patterns = load_patterns()
    print "Linguistic preprocessing of papers..."
    parse_papers()
    print "Running pattern matching..."
    pattern_matching(patterns)

                