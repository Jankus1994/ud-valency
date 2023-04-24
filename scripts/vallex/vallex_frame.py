class Vallex_frame:
    def __init__( self, lang_mark, frame_id):
        self.lang_mark = lang_mark
        self.id = frame_id
        self.lemmas = None
        self.arguments = []
        self.examples = []
        self.refl = None

        self.matched_ext_frames = []
        self.chosen_matched_ext_frame = None
        self.aligned_val_frames = []  # one or more?
                                    # used for czengvallex evaluation


    def set_lemmas( self, lemmas):
        self.lemmas = lemmas

    def add_argument( self, argument):
        self.arguments.append( argument)

    def add_example( self, example):
        self.examples.append( example)

    def args_to_string( self):
        """ not used now """
        args_str_list = [ arg.to_string() for arg in self.arguments ]
        args_str = ' '.join( args_str_list)
        return args_str

    def set_refl( self, refl):
        """ used only in Vallex (the Czech version) """
        self.refl = refl

    def add_ext_frame( self, ext_frame_type):
        self.matched_ext_frames.append( ext_frame_type)

    def align_val_frame( self, aligned_val_frame):
        self.aligned_val_frames.append( aligned_val_frame)

    def to_string( self):
        lemmas_str = ' '.join( self.lemmas)
        if self.refl:
            lemmas_str += " +R"
        args_str = self.args_to_string()
        return lemmas_str + " | " + args_str #+ "  " + ' '.join( self.examples)
