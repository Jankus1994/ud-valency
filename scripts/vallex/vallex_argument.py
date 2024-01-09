class Vallex_argument:
    def __init__( self):
        self.functor = ""
        self.form = ""
        self.is_obligatory = True
        self.type = ""

        self.matched_ext_args = []
        self.aligned_val_args = []

    def set_functor( self, functor):
        self.functor = functor

    def set_form( self, form):
        self.form = form

    def set_arg_type( self, arg_type):
        self.type = arg_type
        if arg_type in [ "typ", "opt", "non-oblig" ]:
            self.is_obligatory = False
        # else ... arg_type in [ "obl", "oblig" ]

    def add_ext_arg( self, ext_arg):
        self.matched_ext_args.append( ext_arg)

    def align_val_arg( self, aligned_val_arg):
        self.aligned_val_args.append( aligned_val_arg)

    def to_string( self):
        string = self.functor + '-' + self.form
        if not self.is_obligatory:
            string = '(' + string + ')' + '.' + self.type
        return string

