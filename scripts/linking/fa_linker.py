import sys

from linker import *
from collections import defaultdict

class Fa_linker( Linker):
    def __init__( self, onedir_weight=0.5, **kwargs):
        super().__init__( **kwargs)
        self.onedir_weight = onedir_weight


    #
    # def process_verb_index( self, x_verb_index, y_verb_index, y_verb_indices,
    #                         xy_ali_dict, yx_ali_dict):
    #     alis_to_x = [ y_index for y_index in yx_ali_dict.keys()
    #                   if yx_ali_dict[ y_index ] == x_verb_index ]
    #
    #     if y_verb_index in alis_to_x:
    #         yx_points = 3  # the considered counterpart points to x
    #     elif set( alis_to_x) & set( y_verb_indices):
    #         yx_points = 2  # (at least one) another verb points to x
    #     elif alis_to_x:
    #         yx_points = 1  # (at least one) non-verb points to x
    #     else:
    #         yx_points = 0  # nothing points to x
    #
    #
    #     y_index = xy_ali_dict[ x_verb_index ]
    #     if y_index == y_verb_index:
    #         xy_points = 3  # x points to the considered counterpart
    #     elif y_index in y_verb_indices:
    #         xy_points = 2  # x points to another verb
    #     else:
    #         xy_points = 1  # x points to a non-verb
    #
    #     reciproc = 0
    #     if yx_ali_dict[ y_index ] == x_verb_index:
    #         reciproc = 1  # the pointing of x is reciprocated
    #
    #     return [ yx_points, xy_points, reciproc ]

    #def get_score( self, ali_dict, ali_dict_key, _, __):
    #    """ separated for overloading in FaUd_linker """
    #    return ali_dict[ ali_dict_key ]
    # def compute_pair_score( self, xa_verb_index, xb_verb_index, a_verb_indices,
    #                         b_verb_indices, a_b_ali_dict, b_a_ali_dict):
    #     feats = self.get_feats( xa_verb_index, xb_verb_index, a_verb_indices,
    #             b_verb_indices, a_b_ali_dict, b_a_ali_dict)
    #     return feats
    #     score = 0
    #     if feats[ 0 ] == 3 and feats[ 3 ] == 3:
    #         score = 1
    #     elif feats[ 0 ] == 3 or feats[ 3 ] == 3:
    #         score = self.onedir_weight
    #     return score

    def compute_frame_pair_score(self, a_frame_inst, b_frame_inst,
                                 a_b_ali_dict, b_a_ali_dict):
        a_verb_index = a_frame_inst.verb_node_ord
        b_verb_index = b_frame_inst.verb_node_ord

        return self.score_index_pair( a_verb_index, b_verb_index,
                                      a_b_ali_dict, b_a_ali_dict)

    def compute_arg_pair_score( self, a_arg_inst, b_arg_inst,
                                 a_b_ali_dict, b_a_ali_dict):
        a_arg_index = a_arg_inst.token.ord
        b_arg_index = b_arg_inst.token.ord

        return self.score_index_pair( a_arg_index, b_arg_index,
                                      a_b_ali_dict, b_a_ali_dict)

    # def get_feats( self, a_frame_inst, b_frame_inst, a_verb_indices,
    #                         b_verb_indices, a_b_ali_dict, b_a_ali_dict):
    #     xa_verb_index = a_frame_inst.verb_node_ord
    #     xb_verb_index = b_frame_inst.verb_node_ord
    #
    #     return self.score_index_pair( xa_verb_index, xb_verb_index,
    #                                   a_b_ali_dict, b_a_ali_dict)
    #
    #     xa_feats = self.process_verb_index( xa_verb_index, xb_verb_index,
    #             b_verb_indices, a_b_ali_dict, b_a_ali_dict)
    #     xb_feats = self.process_verb_index( xb_verb_index, xa_verb_index,
    #             a_verb_indices, b_a_ali_dict, a_b_ali_dict)
    #     return xa_feats + xb_feats
    #
    # def build_score_table( self, a_frame_insts, b_frame_insts,
    #                        a_b_ali_dict, b_a_ali_dict):
    #
    #     a_verb_indices = [ a_frame_inst.verb_node_ord
    #                        for a_frame_inst in a_frame_insts ]
    #     b_verb_indices = [ b_frame_inst.verb_node_ord
    #                        for b_frame_inst in b_frame_insts ]
    #
    #     #start = datetime.now()
    #     score_table = []
    #     for a_frame_inst in a_frame_insts:
    #         table_row = []
    #
    #         for b_frame_inst in b_frame_insts:
    #             #ali_dict_key = ( a_verb_index, b_verb_index )
    #             score = self.compute_pair_score( a_frame_inst, b_frame_inst,
    #                     a_verb_indices, b_verb_indices, a_b_ali_dict, b_a_ali_dict)
    #             #score = self.get_score( ali_dict, ali_dict_key,
    #             #                        a_frame_inst, b_frame_inst)
    #             table_row.append( score)
    #         score_table.append( table_row)
    #     return score_table

    def score_index_pair( self, a_index, b_index, a_b_ali_dict, b_a_ali_dict):
        ab = a_index in a_b_ali_dict and \
                a_b_ali_dict[ a_index ] == b_index
        ba = b_index in b_a_ali_dict and \
                b_a_ali_dict[ b_index ] == a_index
        if ab and ba:
            return 1
        elif ab or ba:
            return self.onedir_weight
        else:
            return 0

    #def print_stats( self):
    #    print( round( self.cad_time_counter, 3), round( self.bst_time_counter, 3),
    #            file=sys.stderr)

    def get_params( self):
        return "Fa params:  onedir_weight="  + str( self.onedir_weight) + \
                ", threshold=" + str( self.threshold)