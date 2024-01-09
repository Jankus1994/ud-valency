from sent_token import Sent_token


class Frame_type:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self):
        """ called from Frame_extractor._process_frame """
        self.verb_lemma = ""
        self.verb_form = "0"
        self.voice = "0"

        self._insts = []
        self._args = []
        #self.str_args = [] # filled with _args_to_string_list
        self.links = []  # objects pairing corresponding frames from two languages

    @property
    def args( self):  # -> list of frame_type_args
        """ called from another Frame_type._has_identical_args_with and
        reconnect_args and later also from Frame_type_link._link_args
        """
        return self._args
    @args.setter
    def args( self, args):  #void
        """ called from Extraction_finalizer.obl_handling
        when copying frame type in order to find the same one but without
        the oblique argument
        """
        self._args = args
    def add_arg( self, frame_type_arg):  # void
        """ called from Frame_extractor._process_args """
        self.args.append( frame_type_arg)
        frame_type_arg.frame_type = self
    def disconnect_arg( self, frame_type_arg):
        """ called from Extraction_finalizer.finalize_extraction """
        self.args.remove( frame_type_arg)

    def sort_args( self):  # void
        """ called from Frame_extractor._process_frame after processing all args
        important for comparing arguments
        """
        # TODO: maybe move the sorting to frame_arg
        self._args = sorted(self._args, key =
                lambda arg :(arg.deprel, arg.form, arg.case_mark_rels))
 
    # === frame extraction methods ===

    def set_verb_features( self, verb_node):  # void
        """ called from the Frame_extractor._process_frame right after creation"""
        self.verb_lemma = verb_node.lemma

        if verb_node.feats[ "VerbForm" ] != "":
            self.verb_form = verb_node.feats[ "VerbForm" ]

        if verb_node.feats[ "Voice" ] != "":
            self.voice = verb_node.feats[ "Voice" ]


    @property
    def insts( self):  # -> list of Frame_insts
        return self._insts
    def add_inst( self, frame_inst):  # void
        """ called from Frame_extractor._process_args for the first instance
        called from Verb_frame.consider_new_frame_type for instances from identical frames
        """
        self._insts.append( frame_inst)
        frame_inst.type = self



    def is_identical_with( self, another_frame_type):  # -> bool
        """ called from Verb_record.consider_new_frame_type
        checks if this frame is identical with another frame
        """
        if self.verb_lemma == another_frame_type.verb_lemma and \
                self._has_identical_args_with( another_frame_type):
                #self.verb_form == another_frame_type.verb_form and \
                #self.voice == another_frame_type.voice and \
                #self._has_identical_args_with( another_frame_type):
            return True
        return False

    def _has_identical_args_with( self, another_frame_type):  # -> bool
        """ called from is_identical_with
        checks if this frame has identical arguments with another frame
        """
        another_frame_type_args = another_frame_type.args
        if len( self.args) != len( another_frame_type_args):
            return False            

        for i in range( len( self.args)):  # THIS IS NOT BIJECTION
            self_arg = self.args[ i ]
            another_frame_type_arg = another_frame_type_args[ i ]
            if not self_arg.is_identical_with( another_frame_type_arg):
                return False
        return True

    def reconnect_args( self, another_frame_type):  # void
        """ called from Verb_record.consider_new_frame_type
        we suppose, that it has been tested that the frames are identical
        """
        another_frame_type_args = another_frame_type.args
        for i in range( len( self.args)):
            self_frame_type_arg = self.args[ i ]
            another_frame_type_arg = another_frame_type_args[ i ]
            another_frame_type_arg_insts = another_frame_type_arg.insts
            for i, frame_inst_arg in enumerate( another_frame_type_arg_insts):
                self_frame_type_arg.add_inst( frame_inst_arg)

    def finalize_extraction( self, extraction_finalizer):  # void
        """ called from Verb_record.finalize_extraction """
        for frame_type_arg in self.args:
            frame_type_arg.finalize_extraction( extraction_finalizer)

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

    # === html displaying methods ===

    def _args_to_string_list( self):  # -> list of str
        """ called from args_to_one_string
        converts Frame_args to their string representation
        """
        str_args = []
        for arg in self.args:
            arg_string = arg.deprel + '-' + arg.form
            if arg.case_mark_rels != []:
                arg_string += '(' + ','.join( arg.case_mark_rels) + ')'
            str_args.append( arg_string)
        return str_args

    def args_to_one_string( self): # -> str
        """ called from Frame_extractor._print_raw_frames - not used
        and from HTML_creator.process_frame_type
        creates one long string of all frame arguments
        """
        str_args = self._args_to_string_list()
        final_string = ' '.join( str_args)
        return final_string

