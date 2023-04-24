import pickle
from verb_record import Verb_record
from frame_type import Frame_type
from frame_inst_arg import Frame_inst_arg
from frame_type_arg import Frame_type_arg
from frame_inst import Frame_inst
from sent_token import Sent_token

class Frame_extractor():
    """ tool used by frame_aligner to extract frames from each verb node
    may be overloaded with language-specific extractors redefining
    appropropriate (u)deprels and genereal classes in __init__
    the rest of extractor is designed language-independent to remain untouched
    """
    def __init__( self, pickle_output = None):
        """ called from Frame_aligner.__init__ """

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

        self.pickle_output = pickle_output
        self.dict_of_verbs = {}

    def process_tree( self, tree):  # -> list of Frame_inst
        """ called from Frame_aligner.process_bundle """
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
        if node.upos == "VERB":
            if node.lemma in self.dict_of_verbs:
                verb_record = self.dict_of_verbs[ node.lemma ]
            else:
                verb_record = self.verb_record_class( node.lemma)
                self.dict_of_verbs[ node.lemma ] = verb_record
            frame_inst = self._process_frame( verb_record, node)
            return frame_inst
        #elif node.upos == "AUX":
        #    parent_node == node.parent
        #    if parent_node.upos in [ "NOUN", "PRON", "I
        return None

    def _process_frame( self, verb_record, verb_node):  # -> Frame_inst
        """ called from process_node """
        # new frame
        frame_type = self.frame_type_class()
        frame_type.set_verb_features( verb_node)
        frame_inst = self.frame_inst_class()

        # creating and adding args to the frame type/inst
        # creating tokens for example sentence and adding them to frame_inst
        self._process_sentence( frame_type, frame_inst, verb_node)

        frame_type.sort_args()  # important for later frame comparision
        frame_type.add_inst( frame_inst)  # connection between frame type and inst

        # adding the frame to the verb_record
        verb_record.consider_new_frame_type( frame_type) #, frame_inst)

        return frame_inst

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
                    deprel, case_feat, child_rels = self._get_arg_features( sent_node)
                    frame_type_arg = self.frame_type_arg_class( \
                                        deprel, case_feat, child_rels)
                    frame_inst_arg = self.frame_inst_arg_class()
                    if sent_node.udeprel == "obl":
                        # oblique args may or may not be a part of the frame
                        # will be decided later -> not definitive
                        frame_inst_arg.definitive = False
                    token.set_arg( frame_inst_arg)  # connection of token and argument
                    frame_inst.add_arg( frame_inst_arg)
                    frame_type_arg.add_inst( frame_inst_arg)
                    frame_type.add_arg( frame_type_arg)

        frame_inst.sent_tokens = sent_tokens
        frame_inst.verb_node_ord = verb_node.ord
        verb_parent_node = verb_node.parent
        if verb_parent_node is not None:
            frame_inst.verb_parent_ord = verb_parent_node.ord
            frame_inst.verb_parent_upos = verb_parent_node.upos
        frame_inst.verb_deprel = verb_node.deprel
        frame_inst.verb_depth = int( verb_node.get_attrs( [ "depth" ])[ 0 ])
        frame_inst.verb_child_num = int( verb_node.get_attrs( [ "children" ])[ 0 ])

    def _create_token( self, token_node):  # -> Token
        """ called from _process_sentence
        creation and basic initialization of token
        """
        token = Sent_token(token_node.ord, token_node._form)

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

        return deprel, case_feat, child_rels

    def get_dict_of_verbs( self):  # -> dict
        """ called from Frame_aligner._pickle_dict """
        return self.dict_of_verbs