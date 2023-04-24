import sys

from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from cs_module import *
from sent_token import Sent_token

class Extract_control_printer( Frame_extractor):
#class Extract_control_printer( Cs_frame_extractor):
    def __init__( self, control_out_name="", **kwargs):
        self.control_output = sys.stdout
        if control_out_name:
            self.control_output = open( control_out_name, 'w')
        super().__init__( **kwargs)

    def process_tree( self, tree):
        frame_insts = super().process_tree( tree)
        for frame_inst in frame_insts:
            verb_ord = frame_inst.predicate_token.ord
            verb_form = frame_inst.predicate_token._form
            frame_type = frame_inst.type
            verb_lemma = frame_type.verb_lemma
            arg_insts = frame_inst.args
            arg_descrs = [ self.arg_descr( arg_inst) for arg_inst in arg_insts ]
            arg_str = "___".join( arg_descrs)
            sent = ' '.join([token._form for token in frame_inst.sent_tokens])
            print( verb_ord, verb_lemma, verb_form, arg_str, sent,
                   sep='\t', file=self.control_output)
        #print( tree.text, file=self.control_output)
        print( "====", file=self.control_output)
        return frame_insts

    def arg_descr( self, arg_inst):
        arg_token = arg_inst.token._form
        if arg_inst.token.is_elided():
            arg_token = '(' + arg_token + ')'
        arg_type = arg_inst.type
        arg_type_str = arg_type.to_string()
        arg_description = arg_token + ".[" + arg_type_str + "]"
        return arg_description

    def after_process_document( self, doc):  # void
        if self.control_output is not sys.stdout:
            self.control_output.close()
