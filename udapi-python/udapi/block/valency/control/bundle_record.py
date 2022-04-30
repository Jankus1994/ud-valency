class Bundle_record:
    def __init__( self):
        self.a_frame_insts = None
        self.a_verbs = None
        self.b_frame_insts = None
        self.b_verbs = None
        self.fa_frame_pairs = None
        self.ud_frame_pairs = None
        self.inter_frame_pairs = None
        self.fa_ext_frame_pairs = None
        self.ud_ext_frame_pairs = None

    def process_a_root( self, a_frame_extractor, a_tree_root):
        self.a_frame_insts = a_frame_extractor.process_tree( a_tree_root)
        self.a_verbs = self.get_verbs( a_tree_root)

    def process_b_root( self, b_frame_extractor, b_tree_root):
        self.b_frame_insts = b_frame_extractor.process_tree( b_tree_root)
        self.b_verbs = self.get_verbs( b_tree_root)

    def perform_pairing( self, fa_linker, ud_linker, word_alignments):
        self.fa_frame_pairs = fa_linker.find_frame_pairs( \
                                self.a_frame_insts, self.b_frame_insts, word_alignments)
        self.ud_frame_pairs = ud_linker.find_frame_pairs( \
                                self.a_frame_insts, self.b_frame_insts, word_alignments)
        self.inter_frame_pairs = list( set( self.fa_frame_pairs) \
                                    & set( self.ud_frame_pairs))
        self.fa_ext_frame_pairs = self.add_nonconflict_pairs( \
                                    self.fa_frame_pairs, self.ud_frame_pairs)
        self.ud_ext_frame_pairs = self.add_nonconflict_pairs( \
                                    self.ud_frame_pairs, self.fa_frame_pairs)

    @staticmethod
    def get_verbs( tree_root):
        nodes = tree_root.descendants
        verbs = [ node for node in nodes if node.upos == "VERB" ]
        return verbs


    @staticmethod
    def add_nonconflict_pairs( primary_pairs, secondary_pairs):
        a_frame_insts = [ frame_inst_pair.a_frame_inst for frame_inst_pair in primary_pairs ]
        b_frame_insts = [ frame_inst_pair.b_frame_inst for frame_inst_pair in primary_pairs ]
        added_pairs = []
        for frame_inst_pair in secondary_pairs:
            a_frame_inst = frame_inst_pair.a_frame_inst
            b_frame_inst = frame_inst_pair.b_frame_inst
            if a_frame_inst not in a_frame_insts and \
                    b_frame_inst not in b_frame_insts:
                added_pairs.append( frame_inst_pair)
                a_frame_insts.append( a_frame_inst)
                b_frame_insts.append( b_frame_inst)
        #print( "Primary length:", len( primary_pairs), sep='\t', file=self.output_file)
        #print( "Secondary length:", len( secondary_pairs), sep='\t', file=self.output_file)
        #print( "Added length:", len( added_pairs), sep='\t', file=self.output_file)
        #print( "", file=self.output_file)
        return primary_pairs + added_pairs
  
