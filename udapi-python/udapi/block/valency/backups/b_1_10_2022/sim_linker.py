from linker import *
from matching_finder import Min_matching_finder
from frame_pair import Frame_pair
from collections import defaultdict

class Sim_linker( Linker):
    def __init__( self, measurer_features=None, treshold=0, **kwargs):
        super().__init__( **kwargs)
        measurer_name = measurer_features[ 0 ]
        measurer_parameters = measurer_features[ 1 ]
        self.measurer = measurer_name( **measurer_parameters)
        self.treshold = treshold
        self.matching_finder = Min_matching_finder()

    def clean_dists_by_treshold( self, dists):
        #return dists
        new_dists = []
        for dist in dists:
            if dist > self.treshold:
                new_dists.append( None)
            else:
                new_dists.append( dist)
        return new_dists

    def build_score_table( self, a_frame_insts, b_frame_insts, _):
        score_table = []
        b_verbs = [ frame_inst.type.verb_lemma for frame_inst in b_frame_insts ]
        for a_frame_inst in a_frame_insts:
            a_verb = a_frame_inst.type.verb_lemma
            dists = self.measurer.compute_dists( a_verb, b_verbs)
            cleaned_dists = self.clean_dists_by_treshold( dists)
            score_table.append( cleaned_dists)
        return score_table

    # def find_frame_pairs(self, a_frame_insts, b_frame_insts, _):
    #     frame_pairs = []
    #
    #     a_to_b_dict, a_to_b_dict_w_dists = self._verb_linking( a_frame_insts, b_frame_insts)
    #     #b_to_a_dict = self._verb_linking( b_frame_insts, a_frame_insts)
    #
    #     for a_frame_inst in a_frame_insts:
    #         str_a_frame_inst = str( a_frame_inst)
    #         #b_frame_insts = a_to_b_dict[ str_a_frame_inst ]
    #         b_frame_insts = a_to_b_dict_w_dists[ str_a_frame_inst ]
    #         if b_frame_insts != []:
    #             # TODO come up with a better solution?
    #             chosen_b_frame_inst, min_dist = b_frame_insts[ 0 ]
    #             frame_pair = Frame_pair( a_frame_inst, chosen_b_frame_inst)
    #             pair_dist = ( frame_pair, min_dist )
    #             frame_pairs.append( frame_pair)
    #             #frame_pairs.append( pair_dist)
    #     return frame_pairs

    # def _verb_linking( self, frst_frame_insts, scnd_frame_insts):
    #     frst_to_scnd_dict = defaultdict( list)
    #     frst_to_scnd_with_dists = defaultdict( list)
    #     scnd_verbs = [ frame_inst.type.verb_lemma for frame_inst in scnd_frame_insts ]
    #     for frst_frame_inst in frst_frame_insts:
    #         frst_verb = frst_frame_inst.type.verb_lemma
    #         str_frst_frame_inst = str( frst_frame_inst)
    #         list_enum_scnd_verbs = list( enumerate( scnd_verbs))
    #         min_distance, closest_scnd_verb_indices = \
    #                 self.measurer.find_closest_verbs( frst_verb, list_enum_scnd_verbs)
    #         for scnd_verb_index in closest_scnd_verb_indices:
    #             scnd_frame_inst = scnd_frame_insts[ scnd_verb_index ]
    #             frst_to_scnd_dict[ str_frst_frame_inst ].append( scnd_frame_inst)
    #             inst_dist = ( scnd_frame_inst, min_distance )
    #             frst_to_scnd_with_dists[ str_frst_frame_inst ].append( inst_dist)
    #     return frst_to_scnd_dict, frst_to_scnd_with_dists
