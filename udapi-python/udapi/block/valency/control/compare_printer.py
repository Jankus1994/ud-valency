"""
"""
import logging
import pickle
import sys

#import os
from udapi.block.valency.control.main_link_control import Main_link_control


class Compare_printer( Main_link_control):
    def __init__( self, corpus_name="", output_folder="", gold_file_name="", **kwargs):
        """ overriden block method """
        super().__init__( **kwargs)

        name = corpus_name + '_'
        self.output = open( output_folder + name + "print", 'w')

        self.gold_code_dict = self.load_gold( gold_file_name)

    @staticmethod
    def load_gold( gold_file_name):
        """
        gets gold frame pair codes
        """
        gold_code_dict = {}
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
                            key = bundle_id + ':' + a_frame_id
                            gold_code_dict[ key ] = b_frame_id
        return gold_code_dict

    def process_bundle( self, bundle):  # void
        """ overriden block method """
        bundle_record = super().process_bundle( bundle)
        auto_frame_pairs_list = [ bundle_record.fa_frame_pairs,
                                  bundle_record.fa_ext_frame_pairs,
                                  bundle_record.ud_ext_frame_pairs ]

        self.print_frames_with_pairing( \
                bundle_record.a_frame_insts, bundle_record.b_frame_insts, bundle.bundle_id, \
                                    self.gold_code_dict, auto_frame_pairs_list)

    def print_frames_with_pairing( self, a_frame_insts, b_frame_insts, sent_number, \
                                   gold_code_dict, auto_frame_pairs_list):
        a_output_text = ""
        pairs_string = ""
        for a_index, a_frame_inst in enumerate( a_frame_insts):
            a_output_text += self.get_frame_string( a_frame_inst, a_index)[ :-1 ]
            a_output_text += '\t' + self.get_pairings( sent_number, a_index, \
                                                       gold_code_dict, auto_frame_pairs_list)

        b_output_text = ""
        for b_index, b_frame_inst in enumerate( b_frame_insts):
            b_output_text += self.get_frame_string( b_frame_inst, b_index)
        if a_output_text or b_output_text:
            print( sent_number, file=self.output)
            print( a_output_text, file=self.output)
            print( "-------", file=self.output)
            print( b_output_text, file=self.output)
            print( "==============", file=self.output)

    @staticmethod
    def get_frame_string( frame_inst, frame_index):
        predicate_form = frame_inst.predicate_token.get_form()
        arg_forms = [ token.get_form() for token in frame_inst.sent_tokens \
                      if token.is_frame_arg() ]
        frame_id = str( frame_index)
        output_string = frame_id + '\t\t' + predicate_form + "___" + '-'.join( arg_forms)
        return output_string + '\n'
        #print( output_string, file=self.output)

    @staticmethod
    def get_pairings( sent_number, a_index, gold_code_dict, auto_frame_pairs_list):
        semicode = str( sent_number) + ':' + str( a_index)
        try:
            gold_b_index = str( gold_code_dict[ semicode ])
        except KeyError:
            gold_b_index = ""
        auto_b_indices = []
        for auto_frame_pairs in auto_frame_pairs_list:
            for auto_frame_pair in auto_frame_pairs:
                if auto_frame_pair.semicode == semicode:
                    auto_b_index = str( auto_frame_pair.b_index)
                    break
            else:
                auto_b_index = ""
            auto_b_indices.append( auto_b_index)
        pairs_string = gold_b_index + '\t' + '\t'.join( auto_b_indices) + '\n'
        return pairs_string

        

