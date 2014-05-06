# -*- coding: utf-8 -*-
"""
Script that automatically annotates papers according to the patterns given.
"""
import os, collections

class Pattern:
    def __init__(self, change_type, is_thing):
        self.change_type = change_type
        self.is_thing = is_thing
        self.subpatterns = list()

target_folder = "DevPapers"

pattern_folder = "patterns"
increase_pattern_file = "increase.ptns"
decrease_pattern_file = "decrease.ptns"
change_pattern_file = "change.ptns"

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
        
    return patterns

if __name__ == "__main__":
    patterns = load_patterns()

    # Do matching
#    papers = [paper for paper in os.listdir(target_folder) if ".txt" in paper]
    
#    for paper in papers:
#        with open(os.path.join(target_folder, paper), 'r') as paperfile:
#            for line in paperfile:
                