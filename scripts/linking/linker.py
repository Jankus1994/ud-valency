from frame_pair import Frame_pair
from matching_finder import Max_matching_finder

#class Frame_pair:
#    def __init__( self, a_frame_type, b_frame_type, a_frame_inst, b_frame_inst):
#        self.a_frame_type = a_frame_type
#        self.b_frame_type = b_frame_type
#        self.a_frame_inst = a_frame_inst
#        self.b_frame_inst = b_frame_inst


class Linker:
    def __init__( self, threshold=0):
        self.log_file = None
        #self.matching_method = greedy_MWB_matching
        #self.matching_method = try_all_matching
        self.matching_finder = Max_matching_finder()
        self.threshold = threshold

    def set_log_file( self, log_file):
        self.log_file = log_file

    def compute_frame_pair_score( self, a_frame_inst, b_frame_inst,
                                 a_b_ali_dict, b_a_ali_dict):
        return 0

    def compute_arg_pair_score( self, a_arg_inst, b_arg_inst,
                                 a_b_ali_dict, b_a_ali_dict):
        return 0

    def compute_frame_pair_score_thresh( self, a_frame_inst, b_frame_inst,
                                         a_b_ali_dict, b_a_ali_dict):
        score = self.compute_frame_pair_score( a_frame_inst, b_frame_inst,
                                               a_b_ali_dict, b_a_ali_dict)
        if score < self.threshold:
            score = 0
        return score

    def compute_arg_pair_score_thresh( self, a_arg_inst, b_arg_inst,
                                       a_b_ali_dict, b_a_ali_dict):
        score = self.compute_arg_pair_score( a_arg_inst, b_arg_inst,
                                               a_b_ali_dict, b_a_ali_dict)
        if score < self.threshold:  # TODO differenitate thresholds
            score = 0
        return score

    def build_score_table( self, a_items, b_items, a_b_ali_dict, b_a_ali_dict,
                           compute_method):
        score_table = []
        for a_item in a_items:
            table_row = []
            for b_item in b_items:
                score = compute_method(
                        a_item, b_item, a_b_ali_dict, b_a_ali_dict)
                table_row.append( score)
            score_table.append( table_row)
        return score_table

        # score_table = [ [ 0 ] * len( b_frame_insts) ] * len(a_items)
        # min_len = min(len(a_items), len(b_frame_insts))
        # for i in range( min_len):
        #     score_table[ i ][ i ] = 1
        # return score_table

    def clean_dists_by_threshold( self, score_table):
        for i in range( len( score_table)):
            for j in range( len( score_table[ i ])):
                score = score_table[ i ][ j ]
                if score < self.threshold:
                    score_table[ i ][ j ] = 0
        return score_table

    def find_frame_pairs( self, a_frame_insts, b_frame_insts,
                          a_b_ali_dict, b_a_ali_dict):
        score_table = self.build_score_table( a_frame_insts, b_frame_insts,
                                              a_b_ali_dict, b_a_ali_dict,
                                              self.compute_frame_pair_score_thresh)

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

    def find_arg_pairs( self, a_arg_insts, b_arg_insts,
                        a_b_ali_dict, b_a_ali_dict):
        score_table = self.build_score_table( a_arg_insts, b_arg_insts,
                                              a_b_ali_dict, b_a_ali_dict,
                                              self.compute_arg_pair_score_thresh)

        chosen_pairs, opt_val = self.matching_finder.find_matching(
                len( a_arg_insts), len( b_arg_insts),
                score_table)

        arg_pairs = []
        for a_index, b_index in chosen_pairs:
            a_arg_inst = a_arg_insts[ a_index ]
            b_arg_inst = b_arg_insts[ b_index ]
            #frame_pair = Frame_pair( a_frame_inst, b_frame_inst) TODO
            arg_pair = ( a_arg_inst, b_arg_inst )
            arg_pairs.append( arg_pair)
        return arg_pairs

    def link_sent_frames( self, a_frame_insts, b_frame_insts,
                          a_b_ali_dict, b_a_ali_dict):
        frame_pairs = self.find_frame_pairs( a_frame_insts, b_frame_insts,
                                             a_b_ali_dict, b_a_ali_dict)
        for frame_pair in frame_pairs:
            a_args = frame_pair.a_frame_inst.args
            b_args = frame_pair.b_frame_inst.args
            self.find_arg_pairs( a_args, b_args, a_b_ali_dict, b_a_ali_dict)
        return frame_pairs

    def print_stats( self):
        pass

    def get_params( self):
        return None
