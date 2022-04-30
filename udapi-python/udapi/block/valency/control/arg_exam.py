"""
controls if fast aligner (or another aligner) works well
"""
import logging
import pickle
import sys

#import os
from udapi.block.valency.align_linker import Align_linker
from udapi.block.valency.ud_linker import Ud_linker
from udapi.block.valency.frame_extractor import Frame_extractor
from udapi.block.valency.frame_pair import Frame_pair
from udapi.block.valency.control.ab_counter import AB_counter
from udapi.block.valency.control.main_link_control import Main_link_control
from udapi.block.valency.control.arg_counter import Arg_counter

class Arg_exam( Main_link_control):
    def __init__( self, corpus_name="", output_folder="", gold_file_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        name = corpus_name + '_'
        self.main_output = open( output_folder + name + "main", 'w')
        
        gold_file = open( gold_file_name, 'r')
        self.gold_frame_pair_codes = self.load_gold_codes( gold_file_name)

        # cummulative frame pairs lists
        #self.align_pairs_total = []
        #self.ud_pairs_total = []
        #self.intersect_pairs_total = []
        #self.align_ext_pairs_total = []
        #self.ud_ext_pairs_total = []

        self.fa_arg_counter = Arg_counter( self.main_output)
        self.ud_arg_counter = Arg_counter( self.main_output)
        self.inter_arg_counter = Arg_counter( self.main_output)
        self.align_ext_arg_counter = Arg_counter( self.main_output)
        self.ud_ext_arg_counter = Arg_counter( self.main_output)


    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = super().process_bundle( bundle)

        self.frame_counter.count( bundle_record.a_frame_insts, bundle_record.b_frame_insts)

        #self.align_pairs_total += bundle_record.fa_frame_pairs
        #self.ud_pairs_total += bundle_record.ud_frame_pairs
        #self.intersect_pairs_total += bundle_record.inter_frame_pairs
        #self.align_ext_pairs_total += bundle_record.fa_ext_frame_pairs
        #self.ud_ext_pairs_total += bundle_record.ud_ext_frame_pairs

        self.pair_args( align_frame_pairs, word_alignments, \
                        self.align_arg_counter, self.fa_output)
        self.pair_args( ud_frame_pairs, word_alignments, \
                        self.ud_arg_counter, self.ud_output)
        self.pair_args( intersect_frame_pairs, word_alignments, \
                        self.intersect_arg_counter, self.intersect_output)
        self.pair_args( align_ext_frame_pairs, word_alignments, \
                        self.align_ext_arg_counter, self.fa_ext_output)
        self.pair_args( ud_ext_frame_pairs, word_alignments, \
                        self.ud_ext_arg_counter, self.ud_ext_output)

    def pair_args( self, frame_pairs, word_alignments, counter, output_file):
        counter.frame_pairs_count += len( frame_pairs)
        for frame_pair in frame_pairs:
            a_frame_inst = frame_pair.a_frame_inst
            b_frame_inst = frame_pair.b_frame_inst
 
            align_arg_pairs = self.align_linker.find_arg_pairs( \
                    a_frame_inst, b_frame_inst, word_alignments)
            #ud_arg_deprel_pairs, ud_arg_upos_pairs = \
            ud_arg_deprel_pairs = self.ud_linker.find_arg_pairs( \
                    a_frame_inst, b_frame_inst)
            inter_arg_pairs = list( set( align_arg_pairs) & set( ud_arg_deprel_pairs))
            align_ext_args = self.args_extension( align_arg_pairs, ud_arg_deprel_pairs)
            ud_ext_args = self.args_extension( ud_arg_deprel_pairs, align_arg_pairs)

            counter.align_args_count += len( align_arg_pairs)
            counter.ud_deprel_args_count += len( ud_arg_deprel_pairs)
            counter.inter_args_count += len( inter_arg_pairs)
            counter.align_ext_args_count += len( align_ext_args)
            counter.ud_ext_args_count += len( ud_ext_args)
            #counter.ud_both_args_count += \
            #        len( ud_arg_deprel_pairs) + len( ud_arg_upos_pairs)
            #counter.align_args_dict[ len( align_arg_pairs) ] = \
            #        counter.align_args_dict.get( len( align_arg_pairs), 0) + 1
            #counter.ud_args_dict[ len( ud_arg_deprel_pairs) ] = \
            #        counter.ud_args_dict.get( len( ud_arg_deprel_pairs), 0) + 1
            counter.align_args_dict[ len( align_arg_pairs) ] += 1
            counter.ud_args_dict[ len( ud_arg_deprel_pairs) ] += 1

            self.print_paired_args( align_arg_pairs, "FA: ", output_file)
            self.print_paired_args( ud_arg_deprel_pairs, "UD1:", output_file)
            #self.print_paired_args( ud_arg_deprel_pairs + ud_arg_upos_pairs, \
            #                       "UD2:", output_file)
            print( "", file=output_file)

    def print_paired_args( self, arg_pairs, label, output_file):
        arg_forms = ""
        for a_frame_inst_arg, b_frame_inst_arg in arg_pairs:
            a_token = a_frame_inst_arg.token
            a_form = a_token.get_form()
            b_token = b_frame_inst_arg.token
            b_form = b_token.get_form()
            arg_forms += " " + a_form + '-' + b_form
        print( label, arg_forms, sep='\t', file=output_file)



 

    def after_process_document( self, doc):  # void
        """ overriden block method """
        self.evaluate_frame_pairing_methods( self.main_output)
        self.print_perc_stats( self.main_output)

        super().after_process_document( doc)
