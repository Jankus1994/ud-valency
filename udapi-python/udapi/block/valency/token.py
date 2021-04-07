#from udapi.block.valency.role import Role

class Token:
    def __init__( self):
        """ called from Example_sentence.__init__ """
        self._form = ""
        self._frame_inst_arg = None
        #self.arg_num = None
        self._is_frame_predicate = False
        self._is_elided = False
        self._has_space = True  # for rebuilding the sentence
                           # with punctuation correctly
    def set_form( self, form):  # void
        """ called from Example_sentence.__init__ """
        self._form = form
    def get_form( self):  # -> str
        """ called from HTML_creator.process_inst """
        return self._form

    def set_arg( self, frame_inst_arg): # void
        """ called from Example_sentence.__init__ """
        self._frame_inst_arg = frame_inst_arg
    def is_frame_arg( self):  # -> bool
        """ called from HTML_creator.process_inst """
        return self._frame_inst_arg is not None

    #def set_arg_num( self, arg_num):
    #    self.arg_num = arg_num
    def get_arg_num( self):  # -> int
        """ called from HTML_creator.process_inst """
        arg_num = self._frame_inst_arg.get_arg_num()
        return arg_num

    def mark_frame_predicate( self):  # void
        """ called from Example_sentence.__init__ """
        self._is_frame_predicate = True
    def is_frame_predicate( self):  # -> bool
        """ called from HTML_creator.process_inst """
        return self._is_frame_predicate

    def unmark_space( self):  # void
        """ called from Example_sentence.__init__ """
        self._has_space = False
    def has_space( self):  # -> bool
        """ called from HTML_creator.process_inst """
        return self._has_space

    def mark_elision( self):  # void
        """ called only in languace-specific moduls
        CS: Cs_frame_type.consider_elided_subject
        """
        self._is_elided = True
    def is_elided( self):  # -> bool
        """ called from HTML_creator.process_inst """
        return self._is_elided
