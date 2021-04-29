"""
script to match frames extracted from the corpus by frame extractor (EXT) with the frames from vallex (VAL)
TODO: prepositions and reflexive pronouns
"""

import logging
import pickle
from copy import copy
from vallex_extractor import *


class Vallex_matcher:
    """ MAYBE CLASS IS NOT NEEDED, CHECK AT THE END """
    def __init__( self, ext_dict, val_dict):
        # loading from pickled files
        # there are two one-direction ext dictionaries in the pickle
        # but we suppose they are identical as a symmetrical operation
        # on the two word alignments was performed
        self.ext_dict  = ext_dict
        self.val_dict = val_dict
        self.cases = { "0":"0", "Nom":"1", "Gen":"2", "Dat":"3", \
                "Acc":"4", "Voc":"5", "Loc":"6", "Ins":"7" }

    def match_frames( self, print_stats=True, print_frames=True):
        ext_lemmas = self.ext_dict.keys()
        val_lemmas = self.val_dict.keys()

        ext_lemmaset = set( ext_lemmas)
        val_lemmaset = set( val_lemmas)
        intersection_lemmaset = ext_lemmaset & val_lemmaset
        only_ext_lemmaset = ext_lemmaset - intersection_lemmaset
        only_val_lemmaset = val_lemmaset - intersection_lemmaset

        #for lemma in list( only_val_lemmaset):
        #    print( lemma)

        common_lemmas = sorted( list( intersection_lemmaset))

        #print( common_lemmas)
        ext_frames_num = 0
        val_frames_num = 0
        frame_pairs_num = 0
        paired_ext_frames_num = 0
        paired_val_frames_num = 0
        for lemma in common_lemmas:
            ext_record = self.ext_dict[ lemma ]
            ext_frame_types = ext_record.frame_types
            val_frames = self.val_dict[ lemma ]

            ext_frames_num += len( ext_frame_types)
            val_frames_num += len( val_frames)

            if print_frames:
                print( "\n=================\n")
                print( lemma)
                print( "")
            #if lemma == "watch":
            #    for ext_frame_type in ext_frame_types:
            #        print( ext_frame_type.args_to_one_string())
            #        inst = ext_frame_type.insts[ 0 ]
            #        sent = inst.sentence
            #        print( sent.tokens)
            #    for val_frame in val_frames:
            #        print( val_frame.args_to_string())
            ext_frames_paired = [ False ] * len( ext_frame_types)
            val_frames_paired = [ False ] * len( val_frames)
            for i, ext_frame_type in enumerate( ext_frame_types):
                for j, val_frame in enumerate( val_frames):
                    #print( self.frame_agreement( ext_frame_type, val_frame))
                    if self.frame_agreement( ext_frame_type, val_frame):
                        frame_pairs_num += 1
                        ext_frames_paired[ i ] = True
                        val_frames_paired[ j ] = True
                        val_frame.add_ext_frame( ext_frame_type)
                        if print_frames:
                            print( ext_frame_type.args_to_one_string())
                            print( val_frame.args_to_string())
                            print( "")
                            pass
            paired_ext_frames_num += sum( ext_frames_paired)
            paired_val_frames_num += sum( val_frames_paired)

        if print_stats:
            print( "\n==================================\n\n")
            print( "Numbers of verb lemmas in dictionaries:")
            print( "EXT: ", len( ext_lemmas))
            print( "VAL: ", len( val_lemmas))
            print( "Numbers of unique lemmas in dictionaries:")
            print( "ONLY EXT: ", len( only_ext_lemmaset))
            print( "INTERSEC: ", len( intersection_lemmaset))
            print( "ONLY VAL: ", len( only_val_lemmaset))
            print( "")
            perc_ext = round( 100 / ext_frames_num * paired_ext_frames_num, 2)
            perc_val = round( 100 / val_frames_num * paired_val_frames_num, 2)
            print( "Numbers of frames:")
            print( "TOTAL   EXT: ", ext_frames_num)
            print( "MATCHED EXT: ", paired_ext_frames_num, "...", perc_ext, "%")
            print( "TOTAL   VAL:  ", val_frames_num)
            print( "MATCHED VAL: ", paired_val_frames_num, "...", perc_val, "%")
            print( "PAIRS      : ", frame_pairs_num)


    def function_agreement( self, ext_arg_deprel, val_arg_functor):
        """ not overloaded, same for all child classes
        is it appropriate to compare vallexx semantic functors with UD syntactis deprels?
        always true for now
        """
        return True


    def form_agreement( self, ext_arg_case_feat, ext_arg_case_mark_rels, val_arg_form):
        """ to be overloaded """
        pass

    def arg_agreement( self, ext_arg, val_arg):
        """ !!! TREBA TO PREROBIT, ABY TO BOLO OBECNE !!! 
        NEPRISTUPOVAT K ATRIBUTOM PRIAMO!
        """
        function_agreement = self.function_agreement( ext_arg.deprel, val_arg.functor)
        form_agreement = self.form_agreement( \
                            ext_arg.case_feat, ext_arg.case_mark_rels, val_arg.form)
        # ext_arg does not have oblig attribute
        #oblig_agreement = self.oblig_agreement( ___, val_arg.oblig)
        if function_agreement and form_agreement:
            return True
        else:
            return False

    ## preposition agreement
    #if vallex_arg.prepos_lemma is not None:
    #    for ext_case_mark_rel in ext_frame_arg.case_mark_rels:
    #        ext_deprel, ext_case_mark_lemma = ext_case_mark_rel.split( '-')
    #        if ext_deprel == "case":
    #            if ext_case_mark_lemma == vallex_arg.prepos_lemma:
    #                break
    #            return False
    #
    ## case agreement
    #if ext_frame_arg.case_feat != "" and vallex_arg.case is not None:
    #    ext_frame_case_num = CASES[ ext_frame_arg.case_feat ]
    #    if ext_frame_case_num == vallex_arg.case:
    #        return True
    #    return False

    def frame_agreement( self, ext_frame_type, vallex_record):
        """ for each vallex argument searches a corresponding EXT frame argument
        """
        #agreement = True
        vallex_args = copy( vallex_record.arguments)
        for ext_frame_arg in ext_frame_type.args:
            #arg_matched = False
            for vallex_arg in vallex_args:
                if self.arg_agreement( ext_frame_arg, vallex_arg):
                    vallex_args.remove( vallex_arg)
                    break
            else:
                return False
        # whether the ramaining vallex args are obligatory
        for remaining_vallex_arg in vallex_args:
            if remaining_vallex_arg.is_obligatory:
                return False
        return True

    def get_matched( self):
        id_val_dict = {}
        for val_frame_group in self.val_dict.values():
            for val_frame in val_frame_group:
                val_frame_id = val_frame.id
                if val_frame_id not in id_val_dict:
                    id_val_dict[ val_frame_id ] = val_frame
        dict_pair = ( self.ext_dict, id_val_dict )
        return dict_pair