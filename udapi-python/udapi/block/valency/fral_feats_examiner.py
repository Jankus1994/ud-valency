from udapi.core.block import Block
from frame_extractor import Frame_extractor
from test_gold_linker import Test_gold_linker
from fa_linker import Fa_linker
from ud_linker import Ud_linker
from sim_linker import Sim_linker
from dist_measurer import  Dist_measurer


from statistics import mean
from math import sqrt

class Fral_feats_examiner( Block):
    def __init__( self, align_name="", output_name="", gold_name="", **kwargs):
        super().__init__( **kwargs)
        self.a_frame_extractor = Frame_extractor()
        self.b_frame_extractor = Frame_extractor()

        self.align_file = open( align_name, 'r')
        self.output_file = open( output_name, 'w')
        self.gold_linker = Test_gold_linker()
        self.gold_file = open( gold_name, 'r')
        self.fa_linker = Fa_linker()
        self.ud_linker = Ud_linker()
        self.dist_measurer = Dist_measurer( allow_substitution=True)

        self.output_lists = []

    def get_gold_pairs( self):
        line = self.gold_file.readline()
        fields = line.split( '\t')
        pairs_str = fields[ 0 ]
        pairs = []
        if pairs_str != "":
            pairs = pairs_str.split( ' ')
            mod_pairs = []
            for pair in pairs:
                mod_pair = '-'.join( pair.split( '-')[ :2 ])
                mod_pairs.append( mod_pair)
            pairs = mod_pairs
        return pairs

    def process_bundle( self, bundle):  # void
        """ overriden Block method """
        a_frame_insts = []
        b_frame_insts = []
        for tree_root in bundle.trees:
            if tree_root.zone == self.a_lang_mark:
                a_frame_insts = \
                        self.a_frame_extractor.process_tree( tree_root)
            elif tree_root.zone == self.b_lang_mark:
                b_frame_insts = \
                        self.b_frame_extractor.process_tree( tree_root)
        # for fa linker
        word_alignments = self.align_file.readline().split()
        a_b_ali_dict, b_a_ali_dict = self.fa_linker.create_ali_dicts( word_alignments)
        a_verb_indices = [ a_frame_inst.verb_node_ord
                           for a_frame_inst in a_frame_insts ]
        b_verb_indices = [ b_frame_inst.verb_node_ord
                           for b_frame_inst in b_frame_insts ]
        #

        gold_pairs = self.get_gold_pairs()
        b_verbs = [ frame_inst.type.verb_lemma for frame_inst in b_frame_insts ]
        for a_frame_inst in a_frame_insts:
            a_verb_index = a_frame_inst.verb_node_ord
            a_verb = a_frame_inst.type.verb_lemma
            sim_dists = self.dist_measurer.compute_dists( a_verb, b_verbs)
            for i, b_frame_inst in enumerate( b_frame_insts):
                b_verb_index = b_frame_inst.verb_node_ord
                ali_dict_key = ( a_verb_index, b_verb_index )

                basic_infos = self.gold_linker.get_infos( a_frame_inst, b_frame_inst,
                                                          gold_pairs)
                fa_feats = self.fa_linker.get_feats( a_frame_inst, b_frame_inst,
                        a_verb_indices, b_verb_indices, a_b_ali_dict, b_a_ali_dict)
                ud_feats = self.ud_linker.get_feats( a_frame_inst, b_frame_inst)
                sim_feats = [ sim_dists[ i ] ]
                output_list = basic_infos + fa_feats + ud_feats + sim_feats
                #output_list = basic_infos + ud_feats + sim_feats
                output_line = [ str( round( item, 3)) if type( item) is float
                                else str( item)
                                for item in output_list ]
                self.output_lists.append( output_list)
                print( '\t'.join( output_line), file=self.output_file)

    def after_process_document( self, _):
        self.create_stats( self.output_lists)

    def correlation( self, x_values, y_values):
        x_mean = mean( x_values)
        y_mean = mean( y_values)

        covariance = 0
        x_variance = 0
        y_variance = 0

        for x_val, y_val in zip( x_values, y_values):
            covariance += ( x_val - x_mean ) * ( y_val - y_mean )
            x_variance += ( x_val - x_mean ) ** 2
            y_variance += ( y_val - y_mean ) ** 2

        correlation = covariance / sqrt( x_variance * y_variance)
        return correlation

    def f1_score( self, tt, tf, ft, ff):
        p = tt / ( tt + ft )
        r = tt / ( tt + tf )
        f = 2 * p * r / ( p + r )
        return f


    def bool_stats(self, golds, autos):
        tt = 0
        tf = 0
        ft = 0
        ff = 0
        for gold, auto in zip( golds, autos):
            if gold and auto:
                tt += 1
            elif gold:
                tf += 1
            elif auto:
                ft += 1
            else:
                ff += 1
        corr = round( self.correlation( golds, autos), 3)
        #f1 = round( self.f1_score( tt, tf, ft, ff), 3)
        #return tt, tf, ft, ff, corr
        return corr

    def create_stats(self, output_lists):
        gold_results = [output_line[ 2 ] for output_line in output_lists]
        for field in range( 3, 11):
            feat = [ output_list[ field ] for output_list in output_lists ]
            seat_stats = self.bool_stats( gold_results, feat)
            print( seat_stats)
