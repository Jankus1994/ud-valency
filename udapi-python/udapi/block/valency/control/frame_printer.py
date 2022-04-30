"""
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
from udapi.core.valency.control.main_link_control import Main_link_control


class Frame_printer( Main_link_control):
    def __init__( self, corpus_name="", output_folder="", gold_file_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        name = corpus_name + '_'
        self.output = open( output_folder + name + "print", 'w')
        

    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = super().process_bundle( bundle)

        self.print_frames( \
                bundle_record.a_frame_insts, bundle_record.b_frame_insts, bundle.bundle_id)

    def print_frames( self, a_frame_insts, b_frame_insts, sent_number):
        a_output_text = ""
        for a_index, a_frame_inst in enumerate( a_frame_insts):
            a_output_text += self.get_frame_string( a_frame_inst, a_index)
        b_output_text = ""
        for b_index, b_frame_inst in enumerate( b_frame_insts):
            b_output_text += self.get_frame_string( b_frame_inst, b_index)
        if a_output_text or b_output_text:
            print( sent_number, file=self.output)
            print( a_output_text[ :-1 ], file=self.output)
            print( "-------", file=self.manual_output)
            print( b_output_text[ :-1 ], file=self.output)
            print( "==============", file=self.output)

    def get_frame_string( self, frame_inst, frame_index):
        predicate_form = frame_inst.predicate_token.get_form()
        arg_forms = [ token.get_form() for token in frame_inst.sent_tokens \
                      if token.is_frame_arg() ]
        frame_id = str( frame_index)
        output_string = frame_id + '\t\t' + predicate_form + "___" + '-'.join( arg_forms)
        return output_string + '\n'
        #print( output_string, file=self.manual_output)

        

