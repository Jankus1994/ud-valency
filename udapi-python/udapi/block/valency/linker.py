from frame_pair import Frame_pair
from matching_finder import Max_matching_finder

#class Frame_pair:
#    def __init__( self, a_frame_type, b_frame_type, a_frame_inst, b_frame_inst):
#        self.a_frame_type = a_frame_type
#        self.b_frame_type = b_frame_type
#        self.a_frame_inst = a_frame_inst
#        self.b_frame_inst = b_frame_inst


class Linker:
    def __init__( self):
        self.log_file = None
        #self.matching_method = greedy_MWB_matching
        #self.matching_method = try_all_matching
        self.matching_finder = Max_matching_finder()

    def set_log_file( self, log_file):
        self.log_file = log_file

    def build_score_table( self, a_frame_insts, b_frame_insts, _):
        score_table = [ [ 0 ] * len( b_frame_insts) ] * len( a_frame_insts)
        min_len = min( len(a_frame_insts), len( b_frame_insts))
        for i in range( min_len):
            score_table[ i ][ i ] = 1
        return score_table

    # def build_score_table( self, a_frame_insts, b_frame_insts, word_alignments):
    #     score_table = []
    #     for _ in a_frame_insts:
    #         table_row = []
    #         for __ in b_frame_insts:
    #             score = 1
    #             table_row.append( score)
    #         score_table.append( table_row)
    #     return score_table

    def find_frame_pairs( self, a_frame_insts, b_frame_insts, word_alignments):
        score_table = self.build_score_table( a_frame_insts, b_frame_insts,
                                              word_alignments)

        chosen_pairs, opt_val = self.matching_finder.find_matching(
                len( a_frame_insts), len( b_frame_insts),
                score_table)

        frame_pairs = []
        for a_index, b_index in chosen_pairs:
            a_frame_inst = a_frame_insts[ a_index ]
            b_frame_inst = b_frame_insts[ b_index ]
            frame_pair = Frame_pair( a_frame_inst, b_frame_inst)
            frame_pairs.append( frame_pair)
        return frame_pairs

    def print_stats( self):
        pass
