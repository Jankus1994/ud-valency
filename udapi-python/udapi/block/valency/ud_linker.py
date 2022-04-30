from linker import *
from frame_pair import Frame_pair

class Ud_linker( Linker):
    def find_frame_pairs( self, a_frame_insts, b_frame_insts, word_alignments):
        frame_inst_pairs = []
        if len( a_frame_insts) == 1 and  len( b_frame_insts) == 1:
            a_frame_inst = a_frame_insts[ 0 ]
            b_frame_inst = b_frame_insts[ 0 ]
            #a_frame_type = a_frame_inst.get_type()
            #b_frame_type = b_frame_inst.get_type()
            #frame_pair = Frame_pair( a_frame_type, b_frame_type, a_frame_inst, b_frame_inst)
            frame_inst_pair = Frame_pair( a_frame_inst, b_frame_inst)
            frame_inst_pairs.append( frame_inst_pair)
        elif len( a_frame_insts) > 1 or len( b_frame_insts) > 1:
            a_tuples = self.create_info_tuples( a_frame_insts)
            b_tuples = self.create_info_tuples( b_frame_insts)
            aligned_ords = self.transform_alignments( word_alignments)
            pair_likelihood_table = \
                    self.pair_multiple_frames( a_tuples, b_tuples, aligned_ords)
            frame_inst_pairs = self.find_best_pairs( a_frame_insts, b_frame_insts, \
                                                     pair_likelihood_table)
 
        return frame_inst_pairs

    def create_info_tuples( self, frame_insts):
        tuples = []
        for index, frame_inst in enumerate( frame_insts):
            verb_parent_ord = frame_inst.get_verb_parent_ord()
            verb_parent_upos = frame_inst.get_verb_parent_upos()
            verb_deprel = frame_inst.get_verb_deprel()
            info_tuple = verb_parent_ord, verb_parent_upos, verb_deprel, frame_inst
            tuples.append( info_tuple)
        return tuples

    def transform_alignments( self, word_alignments):
        aligned_ords = []
        for word_alignment in word_alignments:
            a_index_str, b_index_str = word_alignment.split( '-')
            a_index = int( a_index_str)
            b_index = int( b_index_str)
            index_pair = ( a_index + 1, b_index + 1 )
            aligned_ords.append( index_pair)
        return aligned_ords

    def pair_multiple_frames( self, a_tuples, b_tuples, aligned_ords):
        pair_likelihood_table = [ [ 0 ] * len( b_tuples) ] * len( a_tuples)
        for a_index, a_tuple in enumerate( a_tuples):
            for b_index, b_tuple in enumerate( b_tuples):
                pair_likelihood = \
                        self.compute_pair_likelihood( a_tuple, b_tuple, aligned_ords)
                pair_likelihood_table[ a_index ][ b_index ] = pair_likelihood
        return pair_likelihood_table

    def compute_pair_likelihood( self, a_tuple, b_tuple, aligned_ords):
        a_parent_ord, a_parent_upos, a_deprel, a_frame_inst = a_tuple
        b_parent_ord, b_parent_upos, b_deprel, b_frame_inst = b_tuple
        likelihood = 0
        if ( a_parent_ord, b_parent_ord ) in aligned_ords:
            likelihood += 1
        if ( a_parent_upos, b_parent_upos ) in aligned_ords:
            likelihood += 1
        if a_deprel == b_deprel:
            likelihood += 1
        return likelihood

    def find_best_pairs( self, a_frame_insts, b_frame_insts, pair_likelihood_table):
        """" here, a real maximum weighted bipartite matching algorithm
        would be approriate. but it might be too complicated (to implement or import
        and also to run, when thev graph is small). for now, a suboptimal greedy
        algorithm is used """
        pairs_chosen = []
        a_paired = [ False ] * len( a_frame_insts)
        b_paired = [ False ] * len( b_frame_insts)
        desired_likelihoods = [ 3, 2, 1 ]
        for desired_likelihood in desired_likelihoods:
            for a_index, a_frame_inst in enumerate( a_frame_insts):
                if a_paired[ a_index ]:
                    continue
                for b_index, b_frame_inst in enumerate( b_frame_insts):
                    if b_paired[ b_index ]:
                        continue
                    likelihood = pair_likelihood_table[ a_index ][ b_index ]
                    if likelihood == desired_likelihood:
                        frame_pair = Frame_pair( a_frame_inst, b_frame_inst)
                        pairs_chosen.append( frame_pair)
                        a_paired[ a_index ] = True
                        b_paired[ b_index ] = True
                        break
        return pairs_chosen


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

