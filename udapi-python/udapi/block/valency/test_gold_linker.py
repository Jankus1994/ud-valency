from linker import Linker
from fa_linker import Fa_linker
from ud_linker import Ud_linker
from sim_linker import Sim_linker

class Test_gold_linker( Linker):
    #def __init__( self):
    #    super().__init__()
    #    self.gold_file = None

    #def set_gold_file( self, gold_file_name):
    #    self.gold_file = open( gold_file_name, 'r')

    def get_gold_pairs( self ):
        #line = self.gold_file.readline()
        fields = line.split( '\t')
        pairs_str = fields[ 0 ]
        pairs = []
        if pairs_str != "":
            pairs = pairs_str.split( ' ')
            mod_pairs = []
            for pair in pairs:
                mod_pair = '-'.join( pair.split( '-')[ :2 ])
                mod_pairs.append( mod_pair)
            pairs = mod_pairs
        return pairs

    def get_infos( self, a_frame_inst, b_frame_inst, gold_pairs):
        #gold_pairs = self.get_gold_pairs()
        a_verb_lemma = a_frame_inst.type.verb_lemma
        b_verb_lemma = b_frame_inst.type.verb_lemma
        pair = a_verb_lemma + '-' + b_verb_lemma
        result = pair in gold_pairs
        return [ a_verb_lemma, b_verb_lemma, result ]

    def compare_frames_with_results( self, a_frame_insts, b_frame_insts):
        # TODO id miesto slov, parovat tvary miesto lemiem
        gold_pairs = self.get_gold_pairs()
        for a_frame_inst in a_frame_insts:
            a_verb_lemma = a_frame_inst.type.verb_lemma
            for b_frame_inst in b_frame_insts:
                b_verb_lemma = b_frame_inst.type.verb_lemma
                pair = a_verb_lemma + '-' + b_verb_lemma
                result = pair in gold_pairs
                print( a_verb_lemma, b_verb_lemma, result,
                       sep='\t', file=self.log_file)


    def build_score_table( self, a_frame_insts, b_frame_insts, word_alignments):
        self.compare_frames_with_results( a_frame_insts, b_frame_insts)
        return super().build_score_table(
                a_frame_insts, b_frame_insts, word_alignments)

