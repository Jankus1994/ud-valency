class Vallex_argument:
    def __init__( self):
        self.functor = ""
        self.form = ""
        self.is_obligatory = True

    def set_functor( self, functor):
        self.functor = functor

    def set_form( self, form):
        self.form = form

    def set_arg_type( self, arg_type):
        if arg_type in [ "typ", "opt", "non-oblig" ]:
            self.is_obligatory = False
        # else ... arg_type in [ "obl", "oblig" ]

    def to_string( self):
        string = self.functor + '-' + self.form
        if not self.is_obligatory:
            string = '(' + string + ')'
        return string

