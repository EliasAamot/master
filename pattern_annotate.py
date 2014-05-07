# -*- coding: utf-8 -*-
"""
Script that automatically annotates papers according to the patterns given.

TODO :
    negative patterns
"""
import os, collections, subprocess
import xml.etree.ElementTree as ET
import copy

#
# Constants
#

target_folder = "DevPapers"

pattern_folder = "patterns"
increase_pattern_file = "increase.ptns"
decrease_pattern_file = "decrease.ptns"
change_pattern_file = "change.ptns"
neg_change_pattern_file = "neg_change.ptns"

coreNLPpath = os.path.join(os.getcwd(), "sfcnlp")


#
# Data structures
#

class Pattern:
    def __init__(self, change_type, is_thing):
        self.change_type = change_type
        self.is_negative = False
        self.is_thing = is_thing
        self.subpatterns = list()
    def __repr__(self):
        thingstring = "variable"
        if self.is_thing: thingstring = "thing"
        return "Pattern_"+self.change_type+"_"+thingstring+"_"+str(self.subpatterns)

class Node:
    def __init__(self, id, lemma, start, end):
        self.id = id
        self.lemma = lemma
        self.inedges = []
        self.outedges = []
        self.start_offset = start
        self.end_offset = end
    def __repr__(self):
        return str(self.id) + ":" + self.lemma
    def __eq__(self, other):
        return self.id == other.id and self.lemma == other.lemma and self.start_offset == other.start_offset and self.end_offset == other.end_offset
    def __hash__(self):
        return (71 + hash(self.id) + hash(self.lemma) + hash(self.start_offset) + hash(self.end_offset)) / 5
    def get_subtree(self):
        subtree = set()
        subtree.add(self)
        for outedge in self.outedges:
            subtree = subtree.union(outedge.to_node.get_subtree())
        return subtree
    def get_restrictive_subtree(self, blocknode):
        subtree = set()
        subtree.add(self)
        for outedge in self.outedges:
            # Stay away from useless nodes
            if outedge.dep in ['dep', 'appos', 'aux', 'mark', 'expl', 'cop', 'advmod']: continue
            # Stay away from the main trigger node
            if outedge.to_node == blocknode: continue
            subtree = subtree.union(outedge.to_node.get_subtree())
        return subtree
class Edge:
    def __init__(self, to_node, from_id, dep):
        self.to_node = to_node
        self.from_id = from_id
        self.dep = dep
    def __repr__(self):
        return str(self.to_id) + "->" + str(self.from_id) + ":" + str(self.dep)
class Annotator:
    """
        Object to keep track of information required for annotation
    """
    def __init__(self):
        self.annotations = []
        self.max_T_id = 0
        self.max_E_id = 0
        self.max_A_id = 0
    def get_next_T(self):
        self.max_T_id += 1
        return self.max_T_id
    def get_next_E(self):
        self.max_E_id += 1
    def get_next_A(self):
        self.max_A_id += 1
        return self.max_A_id
    def add_annotation(self, annotation):
        self.annotations.append(annotation)


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
    types_and_files = [("Increase", os.path.join(pattern_folder, increase_pattern_file)),
                       ("Decrease", os.path.join(pattern_folder, decrease_pattern_file)),
                       ("Change", os.path.join(pattern_folder, change_pattern_file)),
                       ("NegChange", os.path.join(pattern_folder, neg_change_pattern_file))]
    
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
                    if change_type == "NegChange":
                        new_pattern_change_type = "Change"
                        is_negative = True
                    else:
                        new_pattern_change_type = change_type
                        is_negative = False
                        
                    new_pattern = Pattern(new_pattern_change_type, new_pattern_is_thing)
                    new_pattern.is_negative = is_negative
                    
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
                            elif element in ['T', 'N', 'X', 'Y', 'S']:
                                accept = True
                            # Element is a dependency
                            elif element in ['prep', 'pobj', 'amod', 'nsubj', 'nsubjpass', 
                                             'dobj', 'nn', 'vmod', 'iobj', 'advmod', 'dep',
                                             'xcomp', 'aux', 'ccomp', 'rcmod', 'pcomp',
                                             'appos', 'advcl', 'mark', 'csubj']:
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
                    assert n_s_count > 0, "There needs to be at least one occurence of N or S in a pattern!"
                    
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
        annotator = Annotator()
        paper_text = open(paper[:paper.index('.')]+".txt", 'r').read()
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
            root = Node("0", "ROOT", -1, -1)
            id_to_node_idx["0"] = root
            nodes = [root]
            for token in sentence.iter('token'):
                id = token.attrib['id']
                lemma = token.find('lemma').text
                start = token.find('CharacterOffsetBegin').text
                end = token.find('CharacterOffsetEnd').text
                node = Node(id, lemma, start, end)
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
                    to_node = id_to_node_idx[to_id]
                    edge = Edge(to_node, from_id, dep_type)
                    edges.append(edge)
                    id_to_node_idx[from_id].outedges.append(edge)
                    id_to_node_idx[to_id].inedges.append(edge)
            
            #
            # Pattern matching
            #
            
            # For each of the triggers, see if it is triggered by a lemma
            for trigger in pattern_base:
                if trigger in lemma_to_nodes_idx.keys():
                    # If there is a trigger match, try to match each of the patterns 
                    # TODO ? Only take the first one
                    for pattern in pattern_base[trigger]:
                        # Match all the subpatterns of a pattern to get a match.
                        # Because subpatterns share variables, all matches of a 
                        # subpattern must be stored for the next subpattern,
                        # along with variable assignments, so that the matching
                        # match is not discarded.                
                        
                        subpattern_matchings = []
                        if len(pattern.subpatterns) == 1:
                            subpattern_matchings = subpattern_match(pattern, lemma_to_nodes_idx, id_to_node_idx, pivot='T', pivot_phrase=trigger)
                        else:
                            assert len(pattern.subpatterns)==2, "A pattern needs to consist of one or two subpatterns. No more, no less. Sorry!"
                            # First figure out which element is the unifying element for the two subpatterns
                            join = set(pattern.subpatterns[0]).intersection(pattern.subpatterns[1])
                            if 'T' in join:
                                second_pivot = 'T'
                            elif 'X' in join:
                                second_pivot = 'X'
                            elif 'N' in join:
                                second_pivot = 'N'
                            elif 'S' in join:
                                second_pivot = 'S'
                            else: 
                                # Otherwise the pivot is the string element. Assuming that there is only one string element
                                for j in join:
                                    if j[0] == '"':
                                        second_pivot = j[1:-1]
                                        break
                            
                            # With two subpatterns, first generate all (globally partial) matches of first subpattern
                            partial_matchings = subpattern_match(pattern, lemma_to_nodes_idx, id_to_node_idx, pivot='T', pivot_phrase=trigger, subpattern_number=0)
                            # Then try to make matchings with the second pattern, constrained by the variable matchings given by each partial match
                            for partial_matching in partial_matchings:
                                subpattern_matchings.extend(subpattern_match(pattern, lemma_to_nodes_idx, id_to_node_idx, pivot=second_pivot, variable_assignment=partial_matching, subpattern_number=1))
                            
                            
                        # SEARCH IS COMPLETED, LET'S MAKE SOMETHING OUT OF IT!!!!
                        if subpattern_matchings:
                            # Make one annotation for every match
                            for sm in subpattern_matchings:
                                # Assert that the match is good
                                assert 'S' in sm.keys() or 'N' in sm.keys(), "This match lacks a variable!"
                                assert not ('S' in sm.keys() and 'N' in sm.keys()), "This match has both a N match and a S match. Pattern malformed somehow!"
                                assert 'T' in sm.keys(), "This match lacks a trigger. Pattern malformed somehow!"
                                assert sm['ChangeType'] in ['Increase', 'Decrease', 'Change'], "The change type of the matched pattern is incorrect."
                                assert 'IsThing' in sm.keys(), "The pattern is neither specified as signalling a thing or a variable!"
                                    
                                change_type = sm['ChangeType']
                                event_trigger = sm['T']
                                theme_trigger = None
                                    
                                if 'S' in sm.keys():
                                    theme_trigger = sm['S'].get_subtree()
                                else:
                                    theme_trigger = sm['N'].get_restrictive_subtree(event_trigger)
                                    
                                if sm['IsThing']:
                                    thing_var_type = "Thing"
                                else:
                                    thing_var_type = "Variable"

                                # To find the word sequence for the theme, we use the
                                # following heuristic: Take the longest continous strip
                                # of words and make it into the theme.

                                # Turn theme_trigger into a sorted list
                                theme_list = [(word.id,word.lemma,word) for word in theme_trigger]
                                theme_list = sorted(theme_list, key=lambda v : v[0])
                                # Iterate over sorted list, and extract continous chunks
                                chunks = []
                                current_chunk = [theme_list[0]]
                                for word in theme_list[1:]:
                                    if int(word[0]) == int(current_chunk[-1][0])+1:
                                        current_chunk.append(word)
                                    else:
                                        chunks.append(current_chunk)
                                        current_chunk = [word]
                                chunks.append(current_chunk)
                                # Find the longest chunk to use as trigger
                                chunks = sorted(chunks, key=lambda v : len(' '.join([vv[1] for vv in v])), reverse=True)
                                best_chunk = chunks[0]
                                    
                                # Turn this into a string for the annotation file
                                ttrigger_id = "T" + str(annotator.get_next_T())
                                type_str = thing_var_type
                                start_off = best_chunk[0][2].start_offset
                                end_off = best_chunk[-1][2].end_offset
                                trigger_str = paper_text[int(start_off):int(end_off)]
                                    
                                ann_str = "\t".join([ttrigger_id, type_str+" "+start_off+" "+end_off, trigger_str]).strip("\t")
                                annotator.add_annotation(ann_str)
                                    
                                # Then to find the trigger annotation of the event
                                etrigger_id = "T" + str(annotator.get_next_T())
                                etype_str = change_type
                                start_off = event_trigger.start_offset
                                end_off = event_trigger.end_offset
                                trigger_str = paper_text[int(start_off):int(end_off)]
                                    
                                ann_str = "\t".join([etrigger_id, etype_str+" "+start_off+" "+end_off, trigger_str]).strip("\t")
                                annotator.add_annotation(ann_str)
                                    
                                # ...and the event annotation of the event
                                event_id = "E" + str(annotator.get_next_E())
                                type_str = etype_str
                                type_id = etrigger_id
                                theme_str = "Theme"
                                theme_id = ttrigger_id
                                
                                ann_str = event_id + "\t" + type_str+":"+type_id + " " + theme_str+":"+theme_id
                                annotator.add_annotation(ann_str)
                                    
                                # If the event is negated, store that
                                if sm.get('Negated'):
                                    a_id = "A" + str(annotator.get_next_A())
                                    a_str = "Negated"
                                    e_id = event_id
                                    
                                    ann_str = a_id + "\t" + a_str + " " + e_id
                                    annotator.add_annotation(ann_str)
                                    
        #
        #   When a paper has been successfully pattern matched, 
        #   store what was found in a ANN file
        #
        with open(paper[:paper.index('.')]+".ann", 'w') as annfile:
            for annotation in annotator.annotations:
                annfile.write(annotation+"\n")
                
def subpattern_match(pattern, lemma_to_nodes_idx, id_to_node_idx, pivot='T', pivot_phrase=None, subpattern_number=0, variable_assignment={}):
     # Matching must be conducted as a search.
     # Search state data is :
         #  0) subpattern
         #  1) current position (in subpattern)
         #  2) downwards complete
         #  3) current node
         #  4) variable assignment
     # 
     # Matching is performed by matching one element
     # at the time. Matching starts from T, then
     # works downwards through the dep tree until
     # pattern is fully matched downwards. Then 
     # matching is conducted upwards from T.
     
    assert pivot_phrase or variable_assignment, "You must specify either a pivot phrase or variable assignment to anchor pattern matching!"
                                
    stack = []
    # Create initial search state(s), 
    # If pivot node is not given in variable_assignment, make one possible 
    # pivot node for each maching of the pivot phrase
    if pivot in variable_assignment:
        subpattern = pattern.subpatterns[subpattern_number]
        current_position = subpattern.index(pivot)
        downwards_complete = False
        pivot_node = variable_assignment[pivot]
        start_state = (subpattern,
                       current_position,
                       downwards_complete,
                       pivot_node,
                       variable_assignment)
        stack.append(start_state)
    else:
        subpattern = pattern.subpatterns[subpattern_number]
        current_position = subpattern.index(pivot)
        downwards_complete = False
        pivot_nodes = lemma_to_nodes_idx[pivot_phrase]
        for pivot_node in pivot_nodes:
            start_state = (subpattern,
                           current_position,
                           downwards_complete,
                           pivot_node,
                           {pivot : pivot_node})
            stack.append(start_state)
            
    assert stack
                            
    # Conduct BFS
    subpattern_matchings = []
    while stack:
        # Get the next search state to search from
        current_search_state = stack.pop(0)
#        print current_search_state, trigger
        # Unpack search state
        cur_subpattern = current_search_state[0]
        current_position = current_search_state[1]
        downwards_complete = current_search_state[2]
        current_node = current_search_state[3]
        variable_assignment = current_search_state[4]
        # Find next element to match
        if not downwards_complete:
            current_position += 1
            if current_position == len(cur_subpattern):
                downwards_complete = True
                current_position = cur_subpattern.index(pivot)
        if downwards_complete:
            current_position -= 1
            if current_position < 0:
                # Match completed, store
#                print "Complete match!"
                variable_assignment['ChangeType'] = pattern.change_type
                variable_assignment['IsThing'] = pattern.is_thing
                variable_assignment['Negated'] = pattern.is_negative
                subpattern_matchings.append(variable_assignment)
                continue
        # Try to match next element
        match_target = cur_subpattern[current_position]
        # Match target is a string
        if match_target[0] == '"':
            string_content = match_target[1:-1]
            if string_content == current_node.lemma:
                # If the strings are consistent, store search state
                # Store each string matching node to variable assignments as well. 
                # Beacuse this is required if string matchings unify two subpatterns.
                va = copy.deepcopy(variable_assignment)
                va[current_node.lemma] = current_node
                new_ss = (subpattern,
                          current_position,
                          downwards_complete,
                          current_node,
                          variable_assignment)
                stack.append(new_ss)
            else:
                pass
#                print "String non-match:", string_content, "vs", current_node.lemma
        # Match target is a variable, check assignment consitency
        elif match_target in ['N', 'S', 'T', 'X']:
            if match_target in variable_assignment:
                if variable_assignment[match_target] != current_node:
                    # Variable assignment clash! Do not keep working on this search state
#                    print "Variable clash..."
                    continue
            # Then store variable assignemnt (if consistent, then no problem in overwriting)
            # I use only the root node even with N and S
            variable_assignment = copy.deepcopy(variable_assignment)
            variable_assignment[match_target] = current_node
            # Store search state with matching and variable assignment
            new_ss = (subpattern,
                      current_position,
                      downwards_complete,
                      current_node,
                      variable_assignment)
            stack.append(new_ss)
        # Match target is a dependency
        else:
            # Store a new search state for every instance
            # of this dependency type found
                                    
            # Directions depend on downwards_complete or not
            if not downwards_complete:
                for outedge in current_node.outedges:
                    if outedge.dep == match_target:
                        # Match, create a new search state
                        new_ss = (subpattern, 
                                  current_position,
                                  downwards_complete,
                                  outedge.to_node,
                                  variable_assignment)
                        stack.append(new_ss)
#                    else:
#                        print "Non-match dep edge", outedge.dep, "vs", match_target
            else:
#                print "Baklengs"
                for inedge in current_node.inedges:
                    if inedge.dep == match_target:
                        # Match, create a new search state
                        new_ss = (subpattern, 
                                  current_position,
                                  downwards_complete,
                                  id_to_node_idx[inedge.from_id],
                                  variable_assignment)
                        stack.append(new_ss)
#                    else:
#                        print "Non-match dep edge", inedge.dep, "vs", match_target
    
    return subpattern_matchings
            

if __name__ == "__main__":
    print "Loading in and verifying patterns..."
    patterns = load_patterns()
    print "Linguistic preprocessing of papers..."
    parse_papers()
    print "Running pattern matching..."
    pattern_matching(patterns)

                