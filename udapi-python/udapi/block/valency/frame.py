#from udapi.block.valency.role import Role
from udapi.block.valency.token import Token

class Frame_inst_arg:
    def __init__( self, node):
        """ called from Frame_extractor._process_args """
        #self.frame_inst = None  # this pointer not needed
        self.node = node
        self.frame_type_arg = None
        self.link = None
        #self.arg_num = None

    def set_type_arg( self, frame_type_arg):  # void
        """ called from Frame_type_arg.add_inst """
        self.frame_type_arg = frame_type_arg
    def get_type_arg( self):  # -> Frame_type_arg
        """ called from Frame_inst_link._link_args """
        return self.frame_type_arg

    #def set_frame_inst( self, frame_inst):
    #    """ called from frame_inst.add_arg """
    #    self.frame_inst = frame_inst

    def set_frame_inst_arg_link( self, frame_inst_arg_link):  # void
        """ called from Frame_inst_arg_link.__init__ """
        self.link = frame_inst_arg_link
        #self.arg_num = self.frame_inst_arg_link.get_link_num()

    def get_arg_num( self):  # -> int
        """ called from Token.get_arg_num when creating html page """
        if self.frame_inst_arg_link is not None:
            arg_num = self.link.get_link_num()
            return arg_num
        else:
            return -1
        

class Frame_type_arg:
    """ class representing verb frame argument """
    def __init__( self, node, deprel="", case_feat="", case_mark_rels=[]):
        """ called from Frame_extractor._process_args """
        #self.frame_type = None  # this pointer not needed
        self.links = []
        self.insts = []

        if node is None:  # explicit argument creation
            self.deprel = deprel
            self.case_feat = case_feat
            self.case_mark_rels = case_mark_rels
        else:
            self.deprel = node.deprel

            self.case_feat = node.feats[ "Case" ]
            if self.case_feat == "":
                self.case_feat = "0"

            self.case_mark_rels = []
            for child in node.children:
                if child.deprel in ["case", "mark"]:
                    case_mark_rel = child.deprel + '-' + child.lemma
                    self.case_mark_rels.append( case_mark_rel)

    # === frame extraction methods ===

    #def set_frame_type( self, frame_type):
    #    """ called from frame_type.add_arg """
    #    self.frame_type = frame_type

    def add_inst( self, frame_inst_arg):  # void
        """ called from Frame_extractor._process_args
        and from Frame_type.reconnect_args
        """
        self.insts.append( frame_inst_arg)
        frame_inst_arg.set_type_arg( self)

    def is_identical_with( self, another_frame_arg):  # -> bool
        """ called from Frame_type._has_identical_args_with
        when comparing two frame_types if they are identical
        """
        if self.deprel == another_frame_arg.deprel and \
                self.case_feat == another_frame_arg.case_feat and \
                self.case_mark_rels == another_frame_arg.case_mark_rels:
            return True
        return False

    def get_insts( self):  # -> list of Frame_inst_args
        """ called from Frame_type.reconnect_args
        when reconnecting frame types
        """
        return self.insts

    # === frame linking methods ===

    def add_frame_type_arg_link( self, frame_type_arg_link):  # void
        """ called from Frame_type_arg_link.__init__ """
        if frame_type_arg_link not in self.links:
            # ? control if link includes this arg?
            self.links.append( frame_type_arg_link)

    def find_link_with( self, translation_frame_type_arg):  # -> Frame_type_arg_link
        """ called from Frame_inst_link._link_args """
        for frame_type_arg_link in self.links:
            if frame_type_arg_link.links_type_arg( translation_frame_type_arg):
                return frame_type_arg_link
        return None

    # === dictionary display methods ===

    def to_string( self):  # -> str
        """ called from HTML_creator.process_frame_type_link """
        my_string = self.deprel + '-' + self.case_feat
        if self.case_mark_rels != []:
            my_string += '(' + ','.join( self.case_mark_rels) + ')'
        return my_string


class Example_sentence:
    """ class representing an example sentence for a verb frame
    it contains list of word forms with some information
    used in creation of HTML table
    """
    def __init__( self, verb_node, frame_inst_args, elided_tokens = []):
        """ called from Frame_inst.process_sentence """
        sentence_nodes = verb_node.root.descendants
        #arg_nodes = [ arg.node for arg in frame_inst_args ]
        self.tokens = []
        for node in sentence_nodes:
            token = Token()
            token.set_form( node.form)

            if node is verb_node:
                token.mark_frame_predicate()
            else:
                for frame_inst_arg in frame_inst_args:
                    if node is frame_inst_arg.node:
                        token.set_arg( frame_inst_arg)
                        break

            no_space_after = node.no_space_after #or node is sentence_nodes[ -1 ]
            if no_space_after:
                token.unmark_space()  # space is default otherwise

            self.tokens.append( token)

        # we suppose that the 
        #self.elided_tokens = token_person_1_2.mark_elision()
        #for elided_token in elided_tokens:
        #    elided_token = Token()
        #    # form is supposed to be already set
        #
        #    # space dos not need to be set
        #    elided_token.set_role( Role.ARG)  # we suppose that all elided tokens
        #                                      # are frame arguments
        #    self.elided_tokens.append( elided_token)


class Frame_inst:
    def __init__( self):
        """ called from Frame_extractor._process_frame """
        self.example_sentence_class = Example_sentence
        
        self.frame_type = None
        #self.verb_node = None
        self.args = []
        #self.sentence = None
        iself.link = None
        self.sent_tokens = []

    # === frame extraction methods ===

    def set_type( self, frame_type):  # void
        """ called from Frame_type.add_inst
        once after creation and possibly again after merging of types
        """
        self.frame_type = frame_type

    def process_sentence( self, verb_node, elided_tokens = []):  # void
        """ called from Frame_extractor._process_frame """
        #self.verb_node = verb_node
        #self.sentence = self.example_sentence_class( \
        #                    verb_node, self.args, elided_tokens)

        sent_nodes = verb_node.root.descendants # !!!
        for sent_node in sent_nodes:
            token = Token()
            token.set_form( sent_node.form)

            if sent_node is verb_node:
                token.mark_frame_predicate()
            else:
                for arg in self.args:
                    if sent_node is arg.node:
                        token.set_arg( frame_inst_arg)
                        break

            no_space_after = sent_node.no_space_after #or node is sentence_nodes[ -1 ]
            if no_space_after:
                token.unmark_space()  # space is default otherwise

            self.sent_tokens.append( token)

    def add_arg( self, frame_inst_arg):  # void
        """ called from Frame_extractor._process_args """
        self.args.append( frame_inst_arg)
        #frame_inst_arg.set_frame_inst( self)

    # === frame linking methods ===

    def get_type( self):  # -> Frame_type
        """ called from Frame_aligner._frame_alignment because the alignment
        is between words and senteces, so it obtains aligned frame instances
        and needs to align their types
        """
        return self.frame_type

    def set_frame_inst_link( self, frame_inst_link):  # void
        """ called from Frame_inst_link.__init__ """
        self.link = frame_inst_link
        
    def get_args( self):  # -> list of Frame_inst_arg
        """ called from Frame_inst_link._link_args """
        return self.args


class Frame_type:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self):
        """ called from Frame_extractor._process_frame """
        self.verb_lemma = ""
        self.verb_form = "0"
        self.voice = "0"

        self.insts = []
        self.args = []
        #self.str_args = [] # filled with _args_to_string_list
        self.links = []  # objects pairing corresponding frames from two languages

    def get_args( self):  # -> list of frame_type_args
        """ called from another Frame_type._has_identical_args_with and
        reconnect_args and later also from Frame_type_link._link_args
        """
        return self.args
 
    # === frame extraction methods ===

    def set_verb_features( self, verb_node):  # void
        """ called from the Frame_extractor._process_frame right after creation"""
        self.verb_lemma = verb_node.lemma

        if verb_node.feats[ "VerbForm" ] != "":
            self.verb_form = verb_node.feats[ "VerbForm" ]

        if verb_node.feats[ "Voice" ] != "":
            self.voice = verb_node.feats[ "Voice" ]

    def add_arg( self, frame_type_arg):  # void
        """ called from Frame_extractor._process_args """
        self.args.append( frame_type_arg)
        #frame_type_arg.set_frame_type( self)

    def add_inst( self, frame_inst):  # void
        """ called from Frame_extractor._process_args for the first instance
        called from Verb_frame.consider_new_frame_type for instances from identical frames
        """
        self.insts.append( frame_inst)
        frame_inst.set_type( self)

    def sort_args( self):  # void
        """ called from Frame_extractor._process_frame after processing all args
        important for comparing arguments
        """
        # TODO: maybe move the sorting to frame_arg
        self.args = sorted( self.args, key =
                lambda arg :( arg.deprel, arg.case_feat, arg.case_mark_rels ))

    def is_identical_with( self, another_frame_type):  # -> bool
        """ called from Verb_record.consider_new_frame_type
        checks if this frame is identical with another frame
        """
        if self.verb_lemma == another_frame_type.verb_lemma and \
                self.verb_form == another_frame_type.verb_form and \
                self.voice == another_frame_type.voice and \
                self._has_identical_args_with( another_frame_type):
            return True
        return False

    def _has_identical_args_with( self, another_frame_type):  # -> bool
        """ called from is_identical_with
        checks if this frame has identical arguments with another frame
        """
        another_frame_type_args = another_frame_type.get_args()
        if len( self.args) != len( another_frame_type_args):
            return False            

        for i in range( len( self.args)):
            self_arg = self.args[ i ]
            another_frame_type_arg = another_frame_type_args[ i ]
            if not self_arg.is_identical_with( another_frame_type_arg):
                return False
        return True

    def reconnect_args( self, another_frame_type):  # void
        """ called from Verb_record.consider_new_frame_type
        we suppose, that it has been tested that the frames are identical
        """
        another_frame_type_args = another_frame_type.get_args()
        for i in range( len( self.args)):
            self_arg = self.args[ i ]
            another_frame_type_arg = another_frame_type_args[ i ]
            another_frame_inst_args = another_frame_type_arg.get_insts()
            for another_frame_inst_arg in another_frame_inst_args:
                self_arg.add_inst( another_frame_inst_arg)

    #def _args_to_string_list( self):  # -> list of str
    #    """ called from args_to_one_string
    #    converts Frame_args to their string representation
    #    """
    #    str_args = []
    #    for arg in self.args:
    #        arg_string = arg.deprel + '-' + arg.case_feat
    #        if arg.case_mark_rels != []:
    #            arg_string += '(' + ','.join( arg.case_mark_rels) + ')'
    #        str_args.append( arg_string)
    #    return str_args

    #def args_to_one_string( self): # -> str
    #    """ called from Frame_extractor._print_raw_frames
    #    creates one long string of all frame arguments
    #    """
    #    str_args = self._args_to_string_list()
    #    final_string = ' '.join( str_args)
    #    return final_string

    # === frame linking methods ===

    def add_frame_type_link( self, frame_type_link):  # void
        """ called from Frame_type_link.__init__ """
        if frame_type_link not in self.links:
            #if frame_type_link:
            # !!! maybe we should control if the link includes this frame !!!
            self.links.append( frame_type_link)
    
    def find_link_with( self, translation_frame_type):  # -> Frame_type_link
        """ called from Frame_aligner._frame_alignment """
        for frame_type_link in self.links:
            if frame_type_link.links_type( translation_frame_type):
                return frame_type_link
        return None

