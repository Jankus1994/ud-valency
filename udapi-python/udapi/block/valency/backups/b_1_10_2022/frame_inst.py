class Frame_inst:
    def __init__( self):
        """ called from Frame_extractor._process_frame """
        # self.example_sentence_class = Example_sentence

        self._type = None
        self._verb_node_ord = None
        self._verb_parent_ord = None
        self._verb_parent_upos = None
        self._verb_deprel = None
        self._verb_depth = None
        self._verb_child_num = None
        self._bundle_id = None
        self._index = None  # order of the frame_inst in its sentence
        # self.verb_node_lemma = ""
        self._args = []
        # self.sentence = None
        self._link = None
        self._sent_tokens = []
        self.predicate_token = None
        self._has_modal = False

    @property
    def type( self):  # -> Frame_type
        """ called from Frame_aligner._frame_alignment because the alignment
        is between words and senteces, so it obtains aligned frame instances
        and needs to align their types
        """
        return self._type
    @type.setter
    def type( self, frame_type):  # void
        """ called from Frame_type.add_inst
        once after creation and possibly again after merging of types
        """
        self._type = frame_type

    def set_sent_tokens( self, sent_tokens, elided_tokens=[]):  # void
        """ called from Frame_extractor._process_sentence """
        self._sent_tokens = sent_tokens  # + elided_tokens
        for token in sent_tokens:
            if token.is_frame_predicate():
                self.predicate_token = token

    @property
    def args( self):  # -> list of Frame_inst_args
        """ called from Frame_inst_link._link_args """
        return self._args
    def add_arg( self, frame_inst_arg):  # void
        """ called from Frame_extractor._process_args """
        self._args.append(frame_inst_arg)
        frame_inst_arg.frame_inst = self
    def disconnect_arg( self, frame_inst_arg):
        """ called from Frame_inst_arg.disconnect_yourself """
        self._args.remove(frame_inst_arg)

    @property
    def verb_node_ord( self):  # -> int
        """ called from Frame_aligner._frame_alignment """
        return self._verb_node_ord
    @verb_node_ord.setter
    def verb_node_ord( self, verb_node_ord):
        """ called from Frame_extractor._process_sentence """
        self._verb_node_ord = verb_node_ord

    @property
    def verb_parent_ord( self):  # -> int
        """ called from Ud_linker.create_info_triplets """
        return self._verb_parent_ord
    @verb_parent_ord.setter
    def verb_parent_ord( self, verb_parent_ord):
        """ called from Frame_extractor._process_sentence """
        self._verb_parent_ord = verb_parent_ord

    @property
    def verb_parent_upos( self):  # -> str
        """ called from Ud_linker.create_info_triplets """
        return self._verb_parent_upos
    @verb_parent_upos.setter
    def verb_parent_upos( self, verb_parent_upos):
        """ called from Frame_extractor._process_sentence """
        self._verb_parent_upos = verb_parent_upos

    @property
    def verb_deprel( self):  # -> str
        """ called from Ud_linker.create_info_triplets """
        return self._verb_deprel
    @verb_deprel.setter
    def verb_deprel( self, verb_deprel):
        """ called from Frame_extractor._process_sentence """
        self._verb_deprel = verb_deprel

    @property
    def verb_depth( self): # -> int
        """ depth in dependency tree """
        return self._verb_depth
    @verb_depth.setter
    def verb_depth( self, verb_depth):
        self._verb_depth = verb_depth

    @property
    def verb_child_num( self): # -> int
        """ depth in dependency tree """
        return self._verb_child_num
    @verb_child_num.setter
    def verb_child_num( self, verb_child_num):
        self._verb_child_num = verb_child_num

    @property
    def bundle_id( self):  # -> int
        """ called from Frame_pair.__init__ """
        return self._bundle_id
    @bundle_id.setter
    def bundle_id( self, bundle_id):
        """ called from Frame_extractor.process_tree """
        self._bundle_id = bundle_id

    @property
    def index( self):  # -> int
        """ called from Frame_pair.__init__"""
        return self._index
    @index.setter
    def index( self, index):
        """ called from Frame_extractor.process_tree """
        self._index = index

    @property
    def link( self):
        return self._link
    @link.setter
    def link( self, frame_inst_link):  # void
        """ called from Frame_inst_link.__init__ """
        self._link = frame_inst_link

    @property
    def has_modal( self):
        return self._has_modal
    @has_modal.setter
    def has_modal( self, has_modal):
        """ called from language specific modules when modal verb attached detected"""
        self._has_modal = has_modal
