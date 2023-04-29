class Frame_inst_arg_link:
    def __init__( self, frame_inst_link, a_frame_inst_arg, b_frame_inst_arg):
        """ called from Frame_inst_link._link_args """
        #self.frame_inst_link = frame_inst_link
        self._frame_type_arg_link = None
        self.a_frame_inst_arg = a_frame_inst_arg
        self.b_frame_inst_arg = b_frame_inst_arg

        a_frame_inst_arg.link = self
        b_frame_inst_arg.link = self
        self._link_num = None

    @property
    def frame_type_arg_link( self):  # -> Frame_type_arg_link
        return self._frame_type_arg_link
    @frame_type_arg_link.setter
    def frame_type_arg_link( self, frame_type_arg_link):
        """ called from Frame_type_arg_link.add_frame_inst_arg_link """
        self._frame_type_arg_link = frame_type_arg_link
        self._link_num = frame_type_arg_link.link_num

    @property
    def link_num( self):  # -> int
        """ called from Frame_inst_arg.get_arg_num """
        return self._link_num


class Frame_type_arg_link:
    def __init__( self, frame_type_link, a_frame_type_arg, b_frame_type_arg, link_num):
        """ called from Frame_type_link._link_args """
        #self.frame_type_link = frame_type_link
        self.a_frame_type_arg = a_frame_type_arg
        self.b_frame_type_arg = b_frame_type_arg
        self.frame_inst_arg_links = []
        self._link_num = link_num

        self.a_frame_type_arg.add_frame_type_arg_link( self)
        self.b_frame_type_arg.add_frame_type_arg_link( self)

    def add_frame_inst_arg_link( self, frame_inst_arg_link):  # void
        """ called from Frame_type_link._link_args """
        frame_inst_arg_link.frame_type_arg_link = self
        self.frame_inst_arg_links.append( frame_inst_arg_link)

    def links_type_arg( self, translation_frame_type_arg):  # -> bool
        """ called from Frame_type_arg.find_link_with """ 
        # assymetric !
        return self.b_frame_type_arg == translation_frame_type_arg

    @property
    def link_num( self):  # -> int
        """ called from Frame_inst_arg_link.set_frame_type_arg_link """
        return self._link_num


class Frame_inst_link:
    def __init__( self, frame_type_link, a_frame_inst, b_frame_inst):
        """ called from Frame_type_link.link_frame_insts """
        self.frame_type_link = frame_type_link
        self.a_frame_inst = a_frame_inst
        self.b_frame_inst = b_frame_inst
        self.frame_inst_arg_links = []

        a_frame_inst.link = self
        b_frame_inst.link = self

        self._link_args()

    def _link_args( self):  # -> void
        """ called from __init__ """
        a_frame_inst_args = self.a_frame_inst.args
        b_frame_inst_args = self.b_frame_inst.args

        for a_frame_inst_arg in a_frame_inst_args:
            a_frame_type_arg = a_frame_inst_arg.type
            for b_frame_inst_arg in b_frame_inst_args:
                # ! control if b is not already linked !
                b_frame_type_arg = b_frame_inst_arg.type

                #ab_frame_type_arg_link = self.frame_type_link.get_frame_type_arg_link( \
                #                             a_frame_type_arg, b_frame_type_arg)
                ab_frame_type_arg_link = a_frame_type_arg.find_link_with( \
                                             b_frame_type_arg)
                #print( ab_frame_type_arg_link)

                if ab_frame_type_arg_link is not None:
                    ab_frame_inst_arg_link = \
                            Frame_inst_arg_link( \
                                self, a_frame_inst_arg, b_frame_inst_arg)
                    self.frame_inst_arg_links.append( ab_frame_inst_arg_link)
                    ab_frame_type_arg_link.add_frame_inst_arg_link( \
                            ab_frame_inst_arg_link)
                    break

    def get_other_frame_inst( self, frame_inst):  # -> Frame_type
        """ not used in the general system (called from vallex_evaluator) """
        if frame_inst is self.a_frame_inst:
            return self.b_frame_inst
        elif frame_inst is self.b_frame_inst:
            return self.a_frame_inst
        else:
            return None

    #def add_frame_inst_arg_link( self, 


class Frame_type_link:
    def __init__( self, a_frame_type, b_frame_type):
        """ called from Frame_aligner._frame_alignment """
        self.a_frame_type = a_frame_type
        self.b_frame_type = b_frame_type
        self.frame_type_arg_links = []
        self.frame_inst_links = []

        self.a_frame_type.add_frame_type_link( self)
        self.b_frame_type.add_frame_type_link( self)

        self._link_args()

    def _link_args( self):  # void
        """ called from __init__
        MAIN ARG LINKING PROCEDURE
        IS IT OK THAT IT IS HERE??
        """
        a_frame_type_args = self.a_frame_type.args
        b_frame_type_args = self.b_frame_type.args

        arg_link_num = 0
        for a_frame_type_arg in a_frame_type_args:
            for b_frame_type_arg in b_frame_type_args:
                if a_frame_type_arg.deprel == b_frame_type_arg.deprel:
                    # ! control if b is not already linked !
                    ab_frame_type_arg_link = \
                            Frame_type_arg_link( \
                                self, a_frame_type_arg, b_frame_type_arg, arg_link_num)
                    self.frame_type_arg_links.append( ab_frame_type_arg_link)
                    arg_link_num += 1
                    break

    def link_frame_insts( self, a_frame_inst, b_frame_inst):  # void
        """ called from Frame_aligner._frame_alignment """
        frame_inst_link = Frame_inst_link( self, a_frame_inst, b_frame_inst)
        self.frame_inst_links.append( frame_inst_link)
        #print( len( self.frame_inst_pairs))

    def links_type( self, translation_frame_type):  # -> bool
        """ called from Frame_type.find_link_with """
        # assymetric !
        return self.b_frame_type == translation_frame_type
    
    def get_other_frame_type( self, frame_type):  # -> Frame_type
        """ not used in the general system (called from vallex_evaluator) """
        if frame_type is self.a_frame_type:
            return self.b_frame_type
        elif frame_type is self.b_frame_type:
            return self.a_frame_type
        else:
            return None

    #def get_frame_type_arg_link( self, a_frame_type_arg, b_frame_type_arg):


