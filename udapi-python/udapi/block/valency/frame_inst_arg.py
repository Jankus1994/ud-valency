class Frame_inst_arg:
    def __init__( self, upostag):
        """ called from Frame_extractor._process_sentence """
        self._frame_inst = None
        self._type = None
        self._link = None
        self._token = None
        self._definitive = True
        self._upostag = upostag
        self.used = False

    @property
    def type( self):  # -> Frame_type_arg
        """ called from Frame_inst_link._link_args """
        return self._type
    @type.setter
    def type( self, frame_type_arg):
        """ called from Frame_type_arg.add_inst """
        self._type = frame_type_arg

    @property
    def token( self):  # -> Sent_token
        """ called from Arg_exam.print_paired_args """
        return self._token
    @token.setter
    def token( self, sent_token):  # void
        """ called from Sent_token.set_arg """
        self._token = sent_token

    @property
    def definitive( self):
        return self._definitive
    @definitive.setter
    def definitive( self, definitive):
        self._definitive = definitive

    @property
    def frame_inst( self):  # -> Frame_inst
        return self._frame_inst
    @frame_inst.setter
    def frame_inst( self, frame_inst):
        """ called from Frame_inst.add_arg """
        self._frame_inst = frame_inst
        if frame_inst is not None:
            self.used = True
        #if frame_inst is None:
        #    print(0+"f")

    @property
    def link( self):  # -> Frame_inst_arg_link
        return self._link
    @link.setter
    def link( self, link):
        """ called from Frame_inst_arg_link.__init__ """
        self._link = link
        #self.arg_num = self.frame_inst_arg_link.get_link_num()

    @property
    def arg_num(self):  # -> int
        """ called from Sent_token.get_arg_num when creating html page """
        if self.link is not None:
            arg_num = self.link.get_link_num()
            return arg_num
        else:
            return -1

    @property
    def upostag( self):  # -> str
        return self._upostag
    @upostag.setter
    def upostag( self, upostag):
        self._upostag = upostag

    #def disconnect_yourself( self):
    #    """ called from Frame_type_arg._decide_candidates """
    #    self.frame_inst.remove_arg( self)