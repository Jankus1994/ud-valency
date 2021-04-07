import pickle
from udapi.block.valency.verb_record import Verb_record
from udapi.block.valency.frame import *

class Frame_extractor():
    """ tool used by frame_aligner to extract frames from each verb node
    may be overloaded with language-specific extractors redefining
    appropropriate (u)deprels and genereal classes in __init__
    the rest of extractor is designed language-independent to remain untouched
    """
    def __init__( self, pickle_output = None):
        """ called from Frame_aligner.__init__ """

        self.appropriate_udeprels = \
                [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
        self.appropriate_deprels = [ "obl:arg", "obl:agent" ]

        self.verb_record_class = Verb_record
        self.frame_type_class = Frame_type
        self.frame_inst_class = Frame_inst
        self.frame_type_arg_class = Frame_type_arg
        self.frame_inst_arg_class = Frame_inst_arg

        self.pickle_output = pickle_output
        self.dict_of_verbs = {}

    def process_tree( self, tree):  # -> list of Frame_inst
        """ called from Frame_aligner.process_bundle """
        frame_insts = []
        for node in tree.descendants:
            frame_inst = self._process_node( node)
            if frame_inst is not None:
                frame_insts.append( frame_inst)
        return frame_insts
    
    def _process_node( self, node):  # void
        """ called from process_tree
        searching verbs and calling create_frame for them
        """
        if node.upos == "VERB":
            if node.lemma in self.dict_of_verbs:
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = self.verb_record_class( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            frame_inst = self._process_frame( verb_record, node)
            return frame_inst
        return None

    def _process_frame( self, verb_record, verb_node):  # -> Frame_inst
        """ called from process_node """
        # new frame
        frame_type = self.frame_type_class()
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        self._process_args( frame_type, frame_inst, verb_node)

        frame_type.sort_args()
        frame_inst.process_sentence( verb_node)
        frame_type.add_inst( frame_inst)

        # adding the frame to the verb_record
        verb_record.consider_new_frame_type( frame_type, frame_inst)

        return frame_inst

    def _process_args( self, frame_type, frame_inst, verb_node):  # void
        """ called from _create_frame
        creates args according to given requirements
        and adds them to the type and inst
        """
        for child_node in verb_node.children:
            if child_node.udeprel in self.appropriate_udeprels or \
                    child_node.deprel in self.appropriate_deprels:
                frame_type_arg = self.frame_type_arg_class( child_node)
                frame_type.add_arg( frame_type_arg)
                frame_inst_arg = self.frame_inst_arg_class( child_node)
                frame_inst.add_arg( frame_inst_arg)
                frame_type_arg.add_inst( frame_inst_arg)

    def get_dict_of_verbs( self):
        """ called from Frame_aligner._pickle_dict """
        return self.dict_of_verbs
