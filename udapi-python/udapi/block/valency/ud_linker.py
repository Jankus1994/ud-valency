import sys

from linker import *
from frame_pair import Frame_pair

class Ud_linker( Linker):
    def __init__( self, params_weights=( 1, 1, 1, 1, 1, 1), **kwargs):
        super().__init__( **kwargs)
        self.params_weights = params_weights

    def weigh_params( self, params):
        result = 0
        for param, param_weight in zip( params, self.params_weights):
            result += param * param_weight
        return result

    def compute_pair_score( self, a_frame_inst, b_frame_inst):
        params_points = []

        # verb parent ord
        a_verb_parent_ord = a_frame_inst.verb_parent_ord
        b_verb_parent_ord = b_frame_inst.verb_parent_ord
        ord_dist = abs( a_verb_parent_ord - b_verb_parent_ord)
        params_points.append( 1 / (ord_dist + 1))

        # verb parent upos
        a_verb_parent_upos = a_frame_inst.verb_parent_upos
        b_verb_parent_upos = b_frame_inst.verb_parent_upos
        params_points.append( a_verb_parent_upos == b_verb_parent_upos)

        # verb node ord
        a_verb_node_ord = a_frame_inst.verb_node_ord
        b_verb_node_ord = b_frame_inst.verb_node_ord
        ord_dist = abs( a_verb_node_ord - b_verb_node_ord)
        params_points.append(  1 / (ord_dist + 1))

        # verb deprel
        a_verb_deprel = a_frame_inst.verb_deprel
        b_verb_deprel = b_frame_inst.verb_deprel
        params_points.append( a_verb_deprel == b_verb_deprel)

        # verb depth
        a_verb_depth = a_frame_inst.verb_depth
        b_verb_depth = b_frame_inst.verb_depth
        ord_dist = abs( a_verb_depth - b_verb_depth)
        params_points.append(  1 / (ord_dist + 1))

        # verb child num
        a_verb_child_num = a_frame_inst.verb_child_num
        b_verb_child_num = b_frame_inst.verb_child_num
        ord_dist = abs( a_verb_child_num - b_verb_child_num)
        params_points.append( 1 / (ord_dist + 1))

        return self.weigh_params( params_points)

    def build_score_table( self, a_frame_insts, b_frame_insts, _):
        score_table = []
        for a_frame_inst in a_frame_insts:
            table_row = []
            for b_frame_inst in b_frame_insts:
                score = self.compute_pair_score( a_frame_inst, b_frame_inst)
                table_row.append( score)
            score_table.append( table_row)
        return score_table

    # def find_frame_pairs( self, a_frame_insts, b_frame_insts, _):#word_alignments):
    #     frame_inst_pairs = []
    #     if len( a_frame_insts) == 1 and  len( b_frame_insts) == 1:
    #         a_frame_inst = a_frame_insts[ 0 ]
    #         b_frame_inst = b_frame_insts[ 0 ]
    #         #a_frame_type = a_frame_inst.get_type()
    #         #b_frame_type = b_frame_inst.get_type()
    #         #frame_pair = Frame_pair( a_frame_type, b_frame_type, a_frame_inst, b_frame_inst)
    #         frame_inst_pair = Frame_pair( a_frame_inst, b_frame_inst)
    #         frame_inst_pairs.append( frame_inst_pair)
    #     elif len( a_frame_insts) > 1 or len( b_frame_insts) > 1:
    #         #a_tuples = self.create_info_tuples( a_frame_insts)
    #         #b_tuples = self.create_info_tuples( b_frame_insts)
    #         #aligned_ords = self.transform_alignments( word_alignments)
    #         pair_score_table = \
    #                 self.pair_multiple_frames( a_frame_insts, b_frame_insts)
    #         #pair_likelihood_table = \
    #                 #self.pair_multiple_frames( a_tuples, b_tuples, aligned_ords)
    #         frame_inst_pairs = self.find_best_pairs( a_frame_insts, b_frame_insts, \
    #                                                  pair_score_table)
    #
    #     return frame_inst_pairs

    # def create_info_tuples( self, frame_insts):
    #     tuples = []
    #     for frame_inst in frame_insts:
    #         verb_parent_ord = frame_inst.verb_parent_ord
    #         verb_parent_upos = frame_inst.verb_parent_upos
    #         verb_node = frame_inst.verb_node_ord
    #         verb_deprel = frame_inst.verb_deprel
    #         verb_depth = frame_inst.verb_depth
    #         verb_child_num = frame_inst.verb_child_num
    #         info_tuple = verb_parent_ord, verb_parent_upos, verb_node,\
    #                      verb_deprel, verb_depth, verb_child_num, frame_inst
    #         tuples.append( info_tuple)
    #     return tuples

    # def transform_alignments( self, word_alignments):
    #     aligned_ords = []
    #     for word_alignment in word_alignments:
    #         a_index_str, b_index_str = word_alignment.split( '-')
    #         a_index = int( a_index_str)
    #         b_index = int( b_index_str)
    #         index_pair = ( a_index + 1, b_index + 1 )
    #         aligned_ords.append( index_pair)
    #     return aligned_ords

    # def pair_multiple_frames( self, a_tuples, b_tuples, aligned_ords):
    #     pair_likelihood_table = [ [ 0 ] * len( b_tuples) ] * len( a_tuples)
    #     for a_index, a_tuple in enumerate( a_tuples):
    #         for b_index, b_tuple in enumerate( b_tuples):
    #             pair_likelihood = \
    #                     self.compute_pair_score
    #                     #self.compute_pair_likelihood( a_tuple, b_tuple, aligned_ords)
    #             pair_likelihood_table[ a_index ][ b_index ] = pair_likelihood
    #     return pair_likelihood_table


    # def compute_pair_likelihood( self, a_tuple, b_tuple, aligned_ords):
    #     a_parent_ord, a_parent_upos, a_deprel, a_frame_inst = a_tuple
    #     b_parent_ord, b_parent_upos, b_deprel, b_frame_inst = b_tuple
    #     likelihood = 0
    #     if ( a_parent_ord, b_parent_ord ) in aligned_ords:
    #         likelihood += 1
    #     if ( a_parent_upos, b_parent_upos ) in aligned_ords:
    #         likelihood += 1
    #     if a_deprel == b_deprel:
    #         likelihood += 1
    #     return likelihood


    def find_arg_pairs( self, a_frame_inst, b_frame_inst):
        #a_frame_type = a_frame_inst.get_type()
        #b_frame_type = b_frame_inst.get_type()
        a_frame_inst_args = a_frame_inst.get_args()
        b_frame_inst_args = b_frame_inst.get_args()

        arg_deprel_pairs = []
        arg_upos_pairs = []
        for a_frame_inst_arg in a_frame_inst_args:
            a_frame_type_arg = a_frame_inst_arg.get_type_arg()
            for b_frame_inst_arg in b_frame_inst_args:
                b_frame_type_arg = b_frame_inst_arg.get_type_arg()
                frame_inst_arg_pair = ( a_frame_inst_arg, b_frame_inst_arg )
                if a_frame_type_arg.deprel == b_frame_type_arg.deprel:
                    arg_deprel_pairs.append( frame_inst_arg_pair)
                #if a_frame_type_arg.upos == b_frame_type_arg.upos:
                #    arg_upos_pairs.append( frame_inst_arg_pair)
        return arg_deprel_pairs #, arg_upos_pairs

