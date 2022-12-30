class Frame_type_arg:
    """ class representing verb frame argument """
    def __init__( self, deprel, case_feat, case_mark_rels):
        """ called from Frame_extractor._process_args """
        self._frame_type = None
        self.links = []
        self._insts = []

        self._deprel = deprel
        self._case_feat = case_feat
        self._case_mark_rels = self.process_case_mark_rels( case_mark_rels)

    @staticmethod
    def process_case_mark_rels( case_mark_rels):
        token_forms = []
        for case_mark_rel in case_mark_rels:
            rel_type, token_form = case_mark_rel.split( '-', 1)
            token_forms.append( token_form)
        return token_forms

    # === frame extraction methods ===

    @property
    def frame_type( self):  # -> Frame_type
        return self._frame_type
    @frame_type.setter
    def frame_type( self, frame_type):
        """ called from Frame_type.add_arg """
        self._frame_type = frame_type

    @property
    def insts( self):  # -> list of Frame_inst_args
        """ called from Frame_type.reconnect_args
        when reconnecting frame types
        """
        return self._insts
    @insts.setter
    def insts( self, insts):
        self._insts = insts
    def add_inst( self, frame_inst_arg):  # void
        """ called from Frame_extractor._process_args
        and from Frame_type.reconnect_args
        """
        self._insts.append( frame_inst_arg)
        frame_inst_arg.type = self

    @property
    def deprel( self):
        return self._deprel
    @deprel.setter
    def deprel( self, deprel):
        self._deprel = deprel

    @property
    def case_feat( self):
        return self._case_feat
    @case_feat.setter
    def case_feat( self, case_feat):
        self._case_feat = case_feat

    @property
    def case_mark_rels( self):
        return self._case_mark_rels
    @case_mark_rels.setter
    def case_mark_rels( self, case_mark_rels):
        self._case_mark_rels = case_mark_rels

    def is_identical_with( self, other):  # -> bool
        """ called from Frame_type._has_identical_args_with
        when comparing two frame_types if they are identical
        """
        if self.deprel == other.deprel and \
                self.case_feat == other.case_feat and \
                self.case_mark_rels == other.case_mark_rels:
            return True
        return False

    def finalize_extraction( self, extraction_finalizer):  # void
        """ called from Frame_type.finalize_extraction """
        self._control_obl( extraction_finalizer)

    def _control_obl( self, extraction_finalizer):  # void
        """ called from finalize_extraction """
        if self.deprel == "obl":
            extraction_finalizer.add_obl_arg( self)

    def disconnect_yourself( self):
        """ called from Extraction_finalizer.finalize_extraction """
        for frame_inst_arg in self.insts:
            frame_inst_arg.disconnect_yourself()

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
            #my_string += '(' + ','.join( self.case_mark_rels) + ')'
            my_string += '|' + ','.join( self.case_mark_rels)
        return my_string