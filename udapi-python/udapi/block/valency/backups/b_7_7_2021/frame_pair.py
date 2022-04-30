class Frame_pair:
    def __init__( self, a_frame_inst, b_frame_inst):
        self.a_frame_inst = a_frame_inst
        self.b_frame_inst = b_frame_inst
        a_bundle_id = a_frame_inst.get_bundle_id()
        b_bundle_id = b_frame_inst.get_bundle_id()
        if a_bundle_id != b_bundle_id:
            raise Exception( "Frame pair across bundles.")
        self.bundle_id = a_bundle_id
        self.a_index = a_frame_inst.get_index()
        self.b_index = b_frame_inst.get_index()
        self.code = str( self.bundle_id) + ':' + str( self.a_index) + '-' + str( self.b_index)
        self.semicode = str( self.bundle_id) + ':' + str( self.a_index)

    def __eq__( self, other):
        """ serves for comparison of pairs for given frames extracted
        does not account of differences insideparticular frames
        i.e. one extractor produces frames that lead to frame pairs with unique codes
        but pairs based on different extractors can have identical codes even if they differ
        """
        if isinstance( other, Frame_pair):
            return self.code == other.code
        return False

    def __hash__(self):
        return hash( self.code)
