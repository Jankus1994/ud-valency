class Arg_counter:
    arg_dict_len = 10
    def __init__( self, main_output):
        self.frame_pairs_count = 0

        self.align_args_count = 0
        self.ud_deprel_args_count = 0
        #self.ud_both_args_count = 0
        self.inter_args_count = 0
        self.align_ext_args_count = 0
        self.ud_ext_args_count = 0

        self.main_output = main_output
        self.align_args_dict = [ 0 ] * Arg_counter.arg_dict_len
        self.ud_args_dict = [ 0 ] * Arg_counter.arg_dict_len

    def print_stats( self, a_frames_count, b_frames_count):
        print( self.frame_pairs_count, \
                round( a_frames_count / self.frame_pairs_count, 2), \
                round( b_frames_count / self.frame_pairs_count, 2), \
                sep='\t', file=self.main_output)
        if self.frame_pairs_count != 0:
            align_mean = round( self.align_args_count / self.frame_pairs_count, 2)
            ud_deprel_mean = round( self.ud_deprel_args_count / self.frame_pairs_count, 2)
            #ud_both_mean = round( self.ud_both_args_count / frames_num, 2)
        else:
            align_mean = "NaN"
            ud_deprel_mean = "NaN"
            #ud_both_mean = "NaN"

        print( "FA sum: ", self.align_args_count, "mean:", align_mean, \
                sep='\t', file=self.main_output)
        print( "UD sum:", self.ud_deprel_args_count, "mean:", ud_deprel_mean, \
                sep='\t', file=self.main_output)
        #print( "UD2 sum:", self.ud_both_args_count, "mean:", ud_both_mean, \
        #        sep='\t', file=self.main_output)
        align_arg_str = ""
        ud_arg_str = ""
        for arg_num in range(Arg_counter.arg_dict_len):
            if self.align_args_dict[ arg_num ] > 0:
                align_arg_str += " " + str( arg_num) + \
                        ":" + str( self.align_args_dict[ arg_num ])
            if self.ud_args_dict[ arg_num ] > 0:
                ud_arg_str +=  " " + str( arg_num) + \
                        ":" + str( self.ud_args_dict[ arg_num ])

        print( "FA args:", align_arg_str, sep='\t', file=self.main_output)
        print( "UD args:", ud_arg_str, sep='\t', file=self.main_output)
        print( "IN: ", self.inter_args_count, sep='\t', file=self.main_output)
        print("FA_ext: ", self.align_ext_args_count, sep='\t', file=self.main_output) 
