"""
script to match frames extracted from the corpus by my extractor with the frames from vallex
TODO: prepositions and reflexive pronouns
"""

import pickle
import sys
from copy import copy
from vallex_extractor import *

CASES = { "0":"0", "Nom":"1", "Gen":"2", "Dat":"3", "Acc":"4", "Loc":"6", "Ins":"7" }

def arg_agreement( cs_frame_arg, vallex_arg):
    if cs_frame_arg.case_feat != "" and vallex_arg.case is not None:
        cs_frame_case_num = CASES[ cs_frame_arg.case_feat ]
        if cs_frame_case_num == vallex_arg.case:
            return True
        return False

def frame_agreement( cs_frame_type, vallex_record):
    agreement = True
    vallex_args = copy( vallex_record.arguments)
    for cs_frame_arg in cs_frame_type.arguments:
        arg_matched = False
        for vallex_arg in vallex_args:
            if arg_agreement( cs_frame_arg, vallex_arg):
                vallex_args.remove( vallex_arg)
                break
        else:
            return False
    for left_vallex_arg in vallex_args:
        if left_vallex_arg.arg_type == "obl":
            return False
    return True


if len( sys.argv) < 3:
    exit()

# loading from pickled files
cs_verb_dict, _ = pickle.load( open( sys.argv[ 1 ], "rb" ))
vallex_dict = pickle.load( open( sys.argv[ 2 ], "rb" ))

cs_verb_lemmas = cs_verb_dict.keys()
cs_verb_lemmaset = set( cs_verb_lemmas)

vallex_lemmas = vallex_dict.keys()
vallex_lemmaset = set( vallex_lemmas)

intersection_lemmaset = cs_verb_lemmaset & vallex_lemmaset

common_lemmas = list( intersection_lemmaset)

#print( common_lemmas)
for lemma in common_lemmas:
    cs_verb_record = cs_verb_dict[ lemma ]
    cs_frame_types = cs_verb_record.frame_types
    vallex_records = vallex_dict[ lemma ]
    
    print( "\n=================\n")
    print( lemma)
    print( "")
    for cs_frame_type in cs_frame_types:
        for vallex_record in vallex_records:
            if frame_agreement( cs_frame_type, vallex_record):
                print( cs_frame_type.args_to_one_string())
                print( vallex_record.args_string())
                print( "")
    
    
