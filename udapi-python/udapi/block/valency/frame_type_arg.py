class Frame_type_arg:
    """ class representing verb frame argument """
    def __init__( self, deprel, form, case_mark_rels):
        """ called from Frame_extractor._process_args """
        self._frame_type = None
        self.links = []
        self._insts = []
        self._id = None
        self._definitive = True
        self.removed = False
        self._deleted = False

        self._deprel = deprel
        self._form = form
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
    def id( self):  # int
        return self._id
    @id.setter
    def id( self, id):
        """ called from Frame_type.sort_args """
        self._id = id

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
        for inst in insts:
            inst.type = self
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
    def form( self):
        return self._form
    @form.setter
    def form( self, form):
        self._form = form

    @property
    def case_mark_rels( self):
        return self._case_mark_rels
    @case_mark_rels.setter
    def case_mark_rels( self, case_mark_rels):
        self._case_mark_rels = case_mark_rels

    @property
    def definitive( self):
        return self._definitive
    @definitive.setter
    def definitive( self, definitive):
        self._definitive = definitive

    @property
    def deleted( self):
        return self._deleted
    @deleted.setter
    def deleted( self, bool_val):
        self._deleted = bool_val

    def get_description( self):
        return self.deprel, self.form, self.case_mark_rels

    def agrees_with( self, deprel, form, case_mark_rels):
        return self.deprel == deprel and self.form == form and \
                self.case_mark_rels == case_mark_rels

    def is_identical_with( self, other):  # -> bool
        """ called from Frame_type._has_identical_args_with
        when comparing two frame_types if they are identical
        """
        if self.deprel == other.deprel and \
                self.form == other.form and \
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

    #def disconnect_yourself( self):
    #    """ called from Extraction_finalizer.finalize_extraction """
    #    for frame_inst_arg in self.insts:
    #        frame_inst_arg.disconnect_yourself()

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

    def id_str( self):
        my_string = self.deprel + '-' + self.form
        if self.case_mark_rels != []:
            my_string += '|' + ','.join( self.case_mark_rels)
        return my_string

    def __str__( self):  # -> str
        """ called from HTML_creator.process_frame_type_link """
        my_string = '{' + str( self.id) + '}'
        my_string += self.id_str()
        if self.definitive == 2:
            my_string = 'X' + my_string
        elif not self.definitive:
            my_string = '*' + my_string
        return my_string