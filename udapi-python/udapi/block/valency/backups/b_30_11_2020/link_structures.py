class Frame_inst_arg_link:
    def __init__( self, frame_inst_link, a_frame_inst_arg, b_frame_inst_arg):
        self.frame_inst_link = frame_inst_link
        self.a_frame_inst_arg = a_frame_inst_arg
        self.b_frame_inst_arg = b_frame_inst_arg


class Frame_type_arg_link:
    def __init__( self, frame_type_link, a_frame_type_arg, b_frame_type_arg):
        self.frame_type_link = frame_type_link
        self.a_frame_type_arg = a_frame_type_arg
        self.b_frame_type_arg = b_frame_type_arg
        self.frame_inst_arg_links = []

    def add_frame_inst_arg_link( self, a_frame_inst_arg, b_frame_inst_arg):
        a_frame_inst_arg.set_frame_arg_link( self)
        b_frame_inst_arg.set_frame_arg_link( self)
        frame_inst_arg_link = Frame_inst_arg_link( \
                self, a_frame_inst_arg, b_frame_inst_arg)
        self.frame_inst_arg_links.append( frame_inst_arg_link)


class Frame_inst_link:
    def __init__( self, frame_type_link, a_frame_inst, b_frame_inst):
        self.frame_type_link = frame_type_link
        self.a_frame_inst = a_frame_inst
        self.b_frame_inst = b_frame_inst
        self.frame_inst_arg_links = []

        a_frame_inst.set_frame_inst_link( self)
        b_frame_inst.set_frame_inst_link( self)

    #def add_frame_inst_arg_link( self, 


class Frame_type_link:
    def __init__( self, a_frame_type, b_frame_type):
        self.a_frame_type = a_frame_type
        self.b_frame_type = b_frame_type
        self.frame_type_arg_links = []
        self.frame_inst_links = []

        self.a_frame_type.add_frame_type_link( self)
        self.b_frame_type.add_frame_type_link( self)

    def link_frame_insts( self, a_frame_inst, b_frame_inst):
        frame_inst_link = Frame_inst_link( self, a_frame_inst, b_frame_inst)
        self.frame_inst_links.append( frame_inst_link)
        #print( len( self.frame_inst_pairs))

    def links_type( self, translation_frame_type):
        # assymetric !
        return self.b_frame_type == translation_frame_type

