"""
controls if fast aligner (or another aligner) works well
"""
import logging
import pickle
import sys
from collections import defaultdict
#import os
from udapi.block.valency.align_linker import Align_linker
from udapi.block.valency.ud_linker import Ud_linker
from udapi.block.valency.frame_extractor import Frame_extractor
from udapi.block.valency.frame_pair import Frame_pair

from udapi.core.block import Block

class Pair_counter:
    """ counts frames pairs aligned with a specific method """
    def __init__( self, name):
        self.name = name
        self.a_left = 0
        self.b_left = 0
        self.pairs = 0
    def count( self, a_items, b_items, pairs):
        a_left = len( a_items) - len( pairs)
        b_left = len( b_items) - len( pairs)
        self.a_left += a_left
        self.b_left += b_left
        self.pairs += len( pairs)
    def print_counts( self, output_file):
        print( ">>> " + self.name, file=output_file)
        a_cover = round( 100 * self.pairs / (self.a_left + self.pairs), 2)
        b_cover = round( 100 * self.pairs / (self.b_left + self.pairs), 2)
        print( "Pairs:", self.pairs, a_cover, b_cover, sep='\t', file=output_file)
        a_percent = 100 - a_cover
        b_percent = 100 - b_cover
        print( "Left (A/B):", self.a_left, a_percent, self.b_left, b_percent, \
                sep='\t', file=output_file)
        print( "------", file=output_file)
 
class Align_control( Block):
    def __init__( self, corpus_name="", align_file_name="", gold_file_name="", \
            output_folder="", a_lang_mark="", b_lang_mark="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        name = corpus_name + '_'
        
        self.manual_output = open( output_folder + name + "manual", 'w')
        self.main_output = open( output_folder + name + "main", 'w')
        self.verb_output = open( output_folder + name + "verbs", 'w')
        self.fa_output = open( output_folder + name + "fa_args", 'w')
        self.ud_output = open( output_folder + name + "ud_args", 'w')
        self.intersect_output = open( output_folder + name + "intersect_args", 'w')
        self.fa_ext_output = open( output_folder + name + "fa_ext_args", 'w')
        self.ud_ext_output = open( output_folder + name + "ud_ext_args", 'w')

        # cummulative frame pairs lists
        self.align_pairs_total = []
        self.ud_pairs_total = []
        self.intersect_pairs_total = []
        self.align_ext_pairs_total = []
        self.ud_ext_pairs_total = []

        # counters
        self.frame_counter = AB_counter( "Frames")
        self.verb_counter = AB_counter( "Verbs")
        self.align_pair_counter = Pair_counter( "FA frame pairs")
        self.ud_pair_counter = Pair_counter( "UD frame pairs")
        self.inter_pair_counter = Pair_counter( "Intersection FA+UD")
        self.ext_align_pair_counter = Pair_counter( "Extended FA <- UD")
        self.ext_ud_pair_counter = Pair_counter( "Extended UD <- FA")

    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = super().process_bundle( bundle)
        
        self.frame_counter.count( a_frame_insts, b_frame_insts)
        #self.verb_counter.count( a_verbs, b_verbs)


        #self.align_frame_count += len( align_frame_pairs)
        #self.ud_frame_count += len( ud_frame_pairs)
        #self.intersect_frame_count += len( intersect_frame_pairs)
        #self.align_ext_frame_count += len( align_ext_frame_pairs)
        #self.ud_ext_frame_count += len( ud_ext_frame_pairs)

    def compare_frame_pairs( self, align_frame_inst_pairs, ud_frame_inst_pairs):
        intersect = list( set( align_frame_inst_pairs) & set( ud_frame_inst_pairs))
        align_only = list( set( align_frame_inst_pairs) - set( ud_frame_inst_pairs))
        ud_only = list( set( ud_frame_inst_pairs) - set( align_frame_inst_pairs))

        intersect_verbs = self.get_verb_form_pairs( intersect)
        align_only_verbs = self.get_verb_form_pairs( align_only)
        ud_only_verbs = self.get_verb_form_pairs( ud_only)

        if intersect_verbs + align_only_verbs + ud_only_verbs != []:
            self.print_verbs( intersect_verbs, 'IN')
            self.print_verbs( align_only_verbs, 'FA')
            self.print_verbs( ud_only_verbs, 'UD')
            print( "", file=self.verb_output)

        
        #self.total_count += 1
        #print( "", file=self.output_file)

    def get_verb_form_pairs( self, frame_pairs):
        verb_form_pairs = []
        for frame_pair in frame_pairs:
            a_frame_inst = frame_pair.a_frame_inst
            b_frame_inst = frame_pair.b_frame_inst
            a_verb = a_frame_inst.sent_tokens[ a_frame_inst.verb_node_ord - 1 ].get_form()
            b_verb = b_frame_inst.sent_tokens[ b_frame_inst.verb_node_ord - 1 ].get_form()
            verb_form_pair = ( a_verb, b_verb )
            verb_form_pairs.append( verb_form_pair)
        return verb_form_pairs

    def print_verbs( self, verb_form_pairs, mark):
        output = ""
        for a_verb_form, b_verb_form in verb_form_pairs:
            output += '  ' + a_verb_form + '-' + b_verb_form
        print( mark+":", len( verb_form_pairs), output, sep='\t', file=self.verb_output)

#    def control_bundle( self, bundle):  # void
#        """ overriden block method """
#        for tree_root in bundle.trees:
#            if tree_root.zone == self.a_lang_mark:
#                a_tokens = tree_root.descendants
#            elif tree_root.zone == self.b_lang_mark:
#                b_tokens = tree_root.descendants
#        
#        word_alignments = self.align_file.readline().split()
#
#        for alignment in alignments:
#            a_index_str, b_index_str = alignment.split( '-')
#            try:
#                a_index = int( a_index_str)
#                b_index = int( b_index_str)
#            except:
#                print( "conv ERROR")
#                exit()
#            a_token = a_tokens[ a_index - 1 ]
#            b_token = b_tokens[ b_index - 1 ]
#            
#            a_descr = a_token.upos + '-' + a_token.deprel
#            b_descr = b_token.upos + '-' + b_token.deprel
#
#            print( a_descr, a_token.form, b_token.form, b_descr, sep='\t', \
#                    file=self.output_file)

    def after_process_document( self, doc):  # void
        """ overriden block method """
        self.frame_counter.print_counts( self.main_output)
        self.verb_counter.print_counts( self.main_output)
        self.align_pair_counter.print_counts( self.main_output)
        self.ud_pair_counter.print_counts( self.main_output)
        self.inter_pair_counter.print_counts( self.main_output)
        self.ext_align_pair_counter.print_counts( self.main_output)
        self.ext_ud_pair_counter.print_counts( self.main_output)
        #print( "FRAMES", file=self.main_output)
        a_frames_count, b_frames_count = self.frame_counter.get_counts()
        print( "FA frame pairs      :", file=self.main_output)
        self.align_arg_counter.print_stats( a_frames_count, b_frames_count)
        print( "", file=self.main_output)

        print( "UD frame pairs      :", file=self.main_output)
        self.ud_arg_counter.print_stats( a_frames_count, b_frames_count)
        print( "", file=self.main_output)

        print( "Intersect frame pairs:", file=self.main_output)
        self.ud_arg_counter.print_stats( a_frames_count, b_frames_count)
        print( "", file=self.main_output)

        print( "Extended frames FA <- UD:", file=self.main_output)
        self.align_ext_arg_counter.print_stats( a_frames_count, b_frames_count)
        print( "", file=self.main_output)

        print( "Extended frames UD <- FA:", file=self.main_output)
        self.ud_ext_arg_counter.print_stats( a_frames_count, b_frames_count)
        print( "", file=self.main_output)

        #print( "ARGS", file=self.main_output)
         
        self.main_output.close()
        self.verb_output.close()
        self.fa_output.close()
        self.ud_output.close()
        self.intersect_output.close()
        self.fa_ext_output.close()
        self.ud_ext_output.close()
        self.manual_output.close()


        #print( self.total_count, self.intersect_count, self.align_count, self.ud_count)
        super().after_process_document( doc)
