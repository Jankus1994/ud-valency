"""
controls if fast aligner (or another aligner) works well
"""
import logging
import pickle
import sys

#import os
from udapi.block.valency.control.ab_counter import AB_counter
from udapi.block.valency.control.main_link_control import Main_link_control


class Gold_frame_eval( Main_link_control):
    def __init__( self, corpus_name="", output_folder="", gold_file_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        name = corpus_name + '_'
        self.main_output = open( output_folder + name + "main", 'w')
        
        gold_file = open( gold_file_name, 'r')
        self.gold_frame_pair_codes = self.load_gold_codes( gold_file_name)

        # cummulative frame pairs lists
        self.align_pairs_total = []
        self.ud_pairs_total = []
        self.intersect_pairs_total = []
        self.align_ext_pairs_total = []
        self.ud_ext_pairs_total = []

        self.frame_counter = AB_counter( "Frames")

    @staticmethod
    def load_gold_codes( gold_file_name):
        """
        gets gold frame pair codes
        """
        gold_frame_pair_codes = []
        with open( gold_file_name, 'r') as gold_file:
            new_bundle = True
            for line in gold_file:
                if "==============" in line:
                    new_bundle = True
                elif new_bundle:
                    new_bundle = False
                    bundle_id = line.split( '\t')[ 0 ]
                else:
                    split_line = line.split( '\t')
                    if len( split_line) > 2:
                        a_frame_id = split_line[ 0 ]
                        b_frame_id = split_line[ 1 ]
                        if a_frame_id != "" and b_frame_id != "":
                            gold_frame_pair_code = \
                                    bundle_id + ':' + a_frame_id + '-' + b_frame_id
                            gold_frame_pair_codes.append( gold_frame_pair_code)
        return gold_frame_pair_codes

    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = super().process_bundle( bundle)

        self.frame_counter.count( bundle_record.a_frame_insts, bundle_record.b_frame_insts)

        self.align_pairs_total += bundle_record.fa_frame_pairs
        self.ud_pairs_total += bundle_record.ud_frame_pairs
        self.intersect_pairs_total += bundle_record.inter_frame_pairs
        self.align_ext_pairs_total += bundle_record.fa_ext_frame_pairs
        self.ud_ext_pairs_total += bundle_record.ud_ext_frame_pairs

        #self.fa_pair_counter.count( a_frame_insts, b_frame_insts, align_frame_pairs)
        #self.ud_pair_counter.count( a_frame_insts, b_frame_insts, ud_frame_pairs)
        #self.compare_frame_pairs( align_frame_pairs, ud_frame_pairs)  # !!!
        #self.inter_pair_counter.count( a_frame_insts, b_frame_insts, intersect_frame_pairs)
        #self.ext_align_pair_counter.count( \
        #        a_frame_insts, b_frame_insts, align_ext_frame_pairs)
        #self.ext_ud_pair_counter.count( \
        #        a_frame_insts, b_frame_insts, ud_ext_frame_pairs)


    def after_process_document( self, doc):  # void
        """ overriden block method """
        self.evaluate_frame_pairing_methods( self.main_output)
        self.print_perc_stats( self.main_output)

        super().after_process_document( doc)

    def evaluate_frame_pairing_methods( self, main_output):
        print( "Evaluation of frame pairs on gold data:", file=main_output)
        align_results = self.evaluate_frame_pairs( self.align_pairs_total)
        self.print_results( "FA", align_results, main_output)

        ud_results = self.evaluate_frame_pairs( self.ud_pairs_total)
        self.print_results( "UD", ud_results, main_output)
        #for fp_code in self.gold_frame_pair_codes: #self.ud_pairs_total:
        #    print( fp_code)

        intersect_results = self.evaluate_frame_pairs( self.intersect_pairs_total)
        self.print_results( "IN", intersect_results, main_output)

        align_ext_results = self.evaluate_frame_pairs( self.align_ext_pairs_total)
        self.print_results( "FA <- UD", align_ext_results, main_output)

        ud_ext_results = self.evaluate_frame_pairs( self.ud_ext_pairs_total)
        self.print_results( "UD <- FA", ud_ext_results, main_output)
        print( "", file=main_output)

    def evaluate_frame_pairs( self, auto_frame_pairs):
        auto_codes = [ frame_pair.code for frame_pair in auto_frame_pairs ]
        intersect_codes = list( set( auto_codes) & set( self.gold_frame_pair_codes))
        #print( len( auto_codes), len( self.gold_frame_pair_codes), len( intersect_codes))
        precision = len( intersect_codes) / len( auto_codes)
        recall = len( intersect_codes) / len( self.gold_frame_pair_codes)
        if precision == 0 and recall == 0:
            f1_score = 0.0
        else:
            f1_score = 2 * precision * recall / ( precision + recall )
        return precision, recall, f1_score

    def print_results( self, name, results, output):
        precision, recall, f1_score = results
        p_str = "P: " + str( round( 100 * precision, 2))
        r_str = "R: " + str( round( 100 * recall, 2))
        f_str = "F: " + str( round( 100 * f1_score, 2))
        print( name + ':', file=output)
        print( p_str + '\t' + r_str + '\t' + f_str, file=output)

    def print_perc_stats( self, main_output):
        a_frame_count = self.frame_counter.a_count
        b_frame_count = self.frame_counter.b_count
        gold_pair_count = len( self.gold_frame_pair_codes)
        align_pair_count = len( self.align_pairs_total)
        ud_pair_count = len( self.ud_pairs_total)
        intersect_pair_count = len( self.intersect_pairs_total)
        align_ext_pair_count = len( self.align_ext_pairs_total)
        ud_ext_pair_count = len( self.ud_ext_pairs_total)
        print( "A", a_frame_count, file=main_output)
        print( "B", b_frame_count, file=main_output)
        self.print_perc_stat( "G", gold_pair_count, a_frame_count, b_frame_count, \
                              main_output)
        self.print_perc_stat( "FA", align_pair_count, a_frame_count, b_frame_count, \
                              main_output)
        self.print_perc_stat( "UD", ud_pair_count, a_frame_count, b_frame_count, \
                              main_output)
        self.print_perc_stat( "IN", intersect_pair_count, a_frame_count, b_frame_count, \
                              main_output)
        self.print_perc_stat( "FA+", align_ext_pair_count, a_frame_count, b_frame_count, \
                              main_output)
        self.print_perc_stat( "UD+", ud_ext_pair_count, a_frame_count, b_frame_count, \
                              main_output)

    def print_perc_stat( self, name, pair_count, a_count, b_count, main_output):
        a_perc = round( 100 * pair_count / a_count, 2)
        b_perc = round( 100 * pair_count / b_count, 2)
        print( name, pair_count, a_perc, b_perc, file=main_output)
