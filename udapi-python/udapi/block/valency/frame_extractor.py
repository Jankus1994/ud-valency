import sys

from udapi.core.block import Block
import pickle
import inspect
from verb_record import Verb_record
from frame_type import Frame_type
from frame_inst_arg import Frame_inst_arg
from frame_type_arg import Frame_type_arg
from frame_inst import Frame_inst
from sent_token import Sent_token
from dict_printer import Dict_printer

class Frame_extractor( Block):
    """ object for monolingual frame extraction
    extracts frames from each verb node

    may be overloaded with language-specific extractors
        redefining appropropriate (u)deprels and genereal classes in __init__
        the rest of extractor is designed language-independent to remain untouched

    2 use cases:
    monolingual - used as separate block
    output: pickle or text

    bilingual - used as tool of frame_aligner
    output: frame_insts from each sentece, dict
    """

    def __init__( self, output_form="text", output_name="", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)
        self.appropriate_udeprels = \
                [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" , "obl" ]
        #self.appropriate_deprels = [ "obl:arg", "obl:agent" ]  # !! move to Czech module
        #self.possible_udeprels = [ "obl" ]
        self.appropriate_child_rels = [ "case", "mark" ]

        self.verb_record_class = Verb_record
        self.frame_type_class = Frame_type
        self.frame_inst_class = Frame_inst
        self.frame_type_arg_class = Frame_type_arg
        self.frame_inst_arg_class = Frame_inst_arg

        self.dict_of_verbs = {}

        # output form - used in after_process_document
        self.output_form = output_form
        self.output_name = output_name

    def process_tree( self, tree):  # -> list of Frame_inst
        """ called as a Block method (monolingual use case)
        or from Frame_aligner.process_bundle
        """
        frame_insts = []
        for node in tree.descendants:
            frame_inst = self._process_node( node)
            if frame_inst is not None:
                frame_insts.append( frame_inst)
        bundle_id = tree.bundle.bundle_id
        for index, frame_inst in enumerate( frame_insts):
            frame_inst.bundle_id = bundle_id
            frame_inst.index = index
        return frame_insts
    
    def _process_node( self, node):  # -> Frame_inst
        """ called from process_tree
        searching verbs and calling create_frame for them
        """
        if self._node_is_appropriate( node):
            if node.lemma in self.dict_of_verbs:
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = self.verb_record_class( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            frame_type, frame_inst = self._process_frame( node)

            # adding the frame to the verb_record
            verb_record.consider_new_frame_type( frame_type)

            return frame_inst
        #elif node.upos == "AUX":
        #    parent_node == node.parent
        #    if parent_node.upos in [ "NOUN", "PRON", "I
        return None

    def _node_is_appropriate( self, node):
        return node.upos == "VERB"

    def _process_frame( self, verb_node):  # -> Frame_inst
        """ called from process_node """
        # new frame
        frame_type = self.frame_type_class()
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        # creating tokens for example sentence and adding them to frame_inst
        self._process_sentence( frame_type, frame_inst, verb_node)

        frame_type.sort_args()  # important for later frame comparision  TODO is thos necessary?
        frame_type.add_inst( frame_inst)  # connection between frame type and inst

        return frame_type, frame_inst

    def _process_sentence( self, frame_type, frame_inst, verb_node):  # void
        """ called from _process_frame
        has several aims:
        - create tokens for being able to reconstruct the example sentcence
        when the dictionary with examples is displayed
        - choose frame arguments according to given requirements
        and connect them with frame objects (both type and inst)
        - create connection between tokens and arguments, so these tokens can be
        marked as arguments when displayed
        """
        sent_nodes = verb_node.root.descendants
        sent_tokens = []
        for sent_node in sent_nodes:
            # sentence tokens
            token = self._create_token( sent_node)
            if sent_node is verb_node:
                token.mark_frame_predicate()
            sent_tokens.append( token)

            # frame arguments
            if sent_node.parent is verb_node:
                #if sent_node.udeprel in self.appropriate_udeprels or \
                #        sent_node.deprel in self.appropriate_deprels:
                if sent_node.udeprel in self.appropriate_udeprels:
                    frame_type_arg, frame_inst_arg = self._process_arg( sent_node)
                    if sent_node.udeprel == "obl":
                        # oblique args may or may not be a part of the frame
                        # will be decided later -> not definitive
                        frame_inst_arg.definitive = False
                    self._connect_frame_with_args( frame_type, frame_inst,
                                                   frame_type_arg, frame_inst_arg,
                                                   token)

        frame_inst.sent_tokens = sent_tokens
        frame_inst.verb_node_ord = verb_node.ord
        verb_parent_node = verb_node.parent
        if verb_parent_node is not None:
            frame_inst.verb_parent_ord = verb_parent_node.ord
            frame_inst.verb_parent_upos = verb_parent_node.upos
        frame_inst.verb_deprel = verb_node.deprel
        frame_inst.verb_depth = int( verb_node.get_attrs( [ "depth" ])[ 0 ])
        frame_inst.verb_child_num = int( verb_node.get_attrs( [ "children" ])[ 0 ])

    def _process_arg( self, arg_node):
        deprel, case_feat, child_rels, upostag = self._get_arg_features( arg_node)
        frame_type_arg = self.frame_type_arg_class(
                            deprel, case_feat, child_rels)
        frame_inst_arg = self.frame_inst_arg_class( upostag)
        return frame_type_arg, frame_inst_arg

    @staticmethod
    def _connect_frame_with_args( frame_type, frame_inst,
                                  frame_type_arg, frame_inst_arg, token):
        token.arg = frame_inst_arg
        frame_inst.add_arg( frame_inst_arg)
        frame_type_arg.add_inst( frame_inst_arg)
        frame_type.add_arg( frame_type_arg)

    def _create_token( self, token_node):  # -> Token
        """ called from _process_sentence
        creation and basic initialization of token
        """
        token = Sent_token( token_node.ord, token_node.form)

        no_space_after = token_node.no_space_after #or node is sentence_nodes[ -1 ]
        if no_space_after:
            token.unmark_space()  # space is default otherwise
        return token

    def _udeprel_is_appropriate( self, udeprel):  # -> bool
        if udeprel in self.appropriate_udeprels:
            return 


    def _get_arg_features( self, node):  # -> tuple ( string, string, list of strings )
        """ called from _process_sentence """
        deprel = node.deprel

        case_feat = node.feats[ "Case" ]
        if case_feat == "":
            case_feat = "0"

        child_rels = []
        for child in node.children:
            if child.deprel in self.appropriate_child_rels:
                child_rel = child.deprel + '-' + child.lemma
                child_rels.append( child_rel)

        upostag = node.upos

        return deprel, case_feat, child_rels, upostag

    def get_dict_of_verbs( self):  # -> dict
        """ called from Frame_aligner._pickle_dict """
        return self.dict_of_verbs

    def after_process_document( self, doc):  # void
        """ overriden block method - monolingual use case"""
        #self._frame_reduction

        if self.output_form == "text":
            Dict_printer.print_mono_frames( self.dict_of_verbs,
                                            out_name=self.output_name)
        elif self.output_form == "stats":
            Dict_printer.print_mono_stats( self.dict_of_verbs,
                                           out_name=self.output_name)
        elif self.output_form == "bin":
            pickle.dump( self.dict_of_verbs, open( self.output_name, 'wb'))

    def _frame_reduction( self):
        for verb_record in self.dict_of_verbs.values():
                verb_record.delete_subframes()  # reducing number of frames before outputting

    def delete_subframes( self):
        """ called from after_process_document on each verb record
        delete all frames that are a
        TODO rozmysli si, co vlastne chces, ci mazat subframy ci superframy
        """
        frame_types = sorted( self.frame_types, key = \
                lambda type:type.args_to_one_string())
        reduced_frame_types = []
        # comparing frames and marking those to delete
        for frame_type in frame_types:
            # a frame should be deleted if it has a superframe
            best_superframe = frame_type
            for potential_superframe in frame_types:
                if potential_superframe.superframe is not None:
                    continue
                if best_superframe.is_subframe_of( potential_superframe) \
                        and self.freq_ratio_is_sufficient(
                                best_superframe, potential_superframe):
                    best_superframe = potential_superframe
            if best_superframe is not frame_type:
                frame_type.superframe = best_superframe

        reduced_frame_types = []
        for frame_type in frame_types:
            if frame_type.superframe is None:
                for subframe in frame_type.subframes:
                    for inst in subframe.insts:
                        frame_type.add_inst( inst)
                reduced_frame_types.append( frame_type)
                frame_type.subframes = []  # the subframes will be deleted

        self.frame_types = reduced_frame_types

    @staticmethod
    def freq_ratio_is_sufficient( subframe, superframe): # -> bool
        """ comparing number of instances of a subframe and a superframe
        returns if the superframe is sufficiently more frequent than the subframe
        """
        coef = 2 # !!!
        if coef * len( subframe.insts) < len( superframe.insts):
            return True
        return False
