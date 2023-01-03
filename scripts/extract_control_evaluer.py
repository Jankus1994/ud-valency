import sys

class Sent_frame:
    def __init__( self, input_line):
        verb_ord, form, lemma, arg_string, sent_tokens = input_line.split( '\t')
        self.ord = verb_ord
        self.form = form
        self.lemma = lemma
        self.args = arg_string.split( "___")


def evaluate( gold_name, auto_name, out_name=""):
    out_file = sys.stdout
    if out_name:
        out_file = open( out_name, 'w')

    with open( gold_name, 'r') as gold_file, \
            open( auto_name, 'r') as auto_file:
        gold_sents = read_sents( gold_file)
        auto_sents = read_sents( auto_file)
        if len( gold_sents) != len( auto_sents):
            print( len( gold_sents), len( auto_sents))
            raise Exception( "different sent num")
        sent_num = len( gold_sents)
        sent_score_sum = 0
        # rel_sum = 0
        # sel_sum = 0
        # com_sum = 0
        # part_rec_sum = 0
        # part_prc_sum = 0
        # part_fsc_sum = 0
        for gold_sent, auto_sent in zip( gold_sents, auto_sents):
            sent_score = compare_sents( gold_sent, auto_sent)
            sent_score_sum += sent_score
        sent_score_mean = sent_score_sum / sent_num
        print( "score:", sent_score_mean)
        #     part_rec = com_num / rel_num if rel_num else 1
        #     part_prc = com_num / sel_num if sel_num else 1
        #     part_fsc = 2 * part_rec * part_prc / ( part_rec + part_prc ) if com_num else 0
        #
        #     rel_sum += rel_num
        #     sel_sum += sel_num
        #     com_sum += com_num
        #     part_rec_sum += part_rec
        #     part_prc_sum += part_prc
        #     part_fsc_sum += part_fsc
        # rel_mean = rel_sum / sent_num
        # sel_mean = sel_sum / sent_num
        # com_mean = com_sum / sent_num
        # rec_1 = com_mean / rel_mean if rel_mean else 1
        # prc_1 = com_mean / sel_mean if sel_mean else 1
        # fsc_1 = 2 * rec_1 * prc_1 / ( rec_1 + prc_1 )
        # rec_2 = part_rec_sum / sent_num
        # prc_2 = part_prc_sum / sent_num
        # fsc_2_1 = part_fsc_sum / sent_num
        # fsc_2_2 = 2 * rec_2 * prc_2 / ( rec_2 + prc_2 )
        # print( "PRF1:", prc_1, rec_1, fsc_1, file=out_file)
        # print( "PRF2:", prc_2, rec_2, fsc_2_1, fsc_2_2, file=out_file)

    if out_name:
        out_file.close()

def compare_sents( gold_sent, auto_sent):
    auto_frames_matched = [ False ] * len( auto_sent)
    score_sum = 0
    common_frames_num = 0
    gold_unmatched_num = 0
    for gold_sent_frame in gold_sent:
        for i, auto_sent_frame in enumerate( auto_sent):
            if auto_frames_matched[ i ]:
                continue
            if gold_sent_frame.ord == auto_sent_frame.ord:
                score = args_equal_score( gold_sent_frame.args, auto_sent_frame.args)
                score_sum += score
                common_frames_num += 1
                auto_frames_matched[ i ] = True
                break
        else:
            gold_unmatched_num += 1
    auto_unmatched_num = sum( [ not item for item in auto_frames_matched ] )
    all_frames_num = common_frames_num + gold_unmatched_num + auto_unmatched_num
    sent_score = score_sum / all_frames_num if all_frames_num else 1
    return sent_score

def args_equal_score( gold_args, auto_args):
    auto_paired = [ False ] * len( auto_args)
    for gold_arg in gold_args:
        for i, auto_arg in enumerate( auto_args):
            if auto_paired[ i ]:
                continue
            if gold_arg == auto_arg:
                auto_paired[ i ] = True
                break
    pairs_num = sum( auto_paired)
    prc = pairs_num / len( auto_args) if auto_args else 1
    rec = pairs_num / len( gold_args) if gold_args else 1
    fsc = 2 * prc * rec / ( prc + rec ) if prc + rec > 0 else 0
    return fsc


def read_sents( in_file):
    sents = []
    while True:
        sent_frames = read_sent_frames( in_file)
        if sent_frames is None:
            break
        sents.append( sent_frames)
    return sents

def read_sent_frames( in_file):
    sent_frames = []
    while True:
        input_line = in_file.readline()
        if input_line == "":  # end of file
            return None
        input_line = input_line.rstrip( '\n')
        if "====" in input_line:
            break
        sent_frame = Sent_frame( input_line)
        sent_frames.append( sent_frame)
    return sent_frames



if __name__ == "__main__":
    gold_name = sys.argv[ 1 ]
    auto_name = sys.argv[ 2 ]
    out_name = ""
    if len( sys.argv) == 4:
        out_name = sys.argv[ 3 ]

    evaluate( gold_name, auto_name, out_name)