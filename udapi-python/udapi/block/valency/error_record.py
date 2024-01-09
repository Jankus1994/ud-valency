class Error_record:
    def __init__( self, sent_id, error_type, error_description):
        """
        types: VRB_RDUN, VRB_MISS, ARG_RDUN, ARG_MISS, ARG_FUNC, ARG_FORM
        """
        self.sent_id = sent_id
        self.type = error_type
        self.desc = error_description

    def log_error( self, file):
        print( self.sent_id, self.type, self.desc, sep='\t', file=file)