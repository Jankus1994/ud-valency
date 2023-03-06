import sys
from collections import Counter

def process_input( input_name, field_num, sep_char):
    all_pairs = []
    with open( input_name, 'r') as input_file:
        for i, line in enumerate(input_file):
            fields = line.split( '\t')
            #print( i, line)
            pairs_str = fields[ field_num ]
            pairs = []
            if pairs_str != "":
                pairs = pairs_str.split( sep_char)
                mod_pairs = []
                for pair in pairs:
                    mod_pair = '-'.join( pair.split( '-')[ :2 ])
                    mod_pairs.append( mod_pair)
                pairs = mod_pairs
            all_pairs.append( pairs)
    return all_pairs

def compare_pairs( all_gold_pairs, all_auto_pairs):
    gold_count = 0
    auto_count = 0
    comm_count = 0
    for gold_pairs, auto_pairs in zip( all_gold_pairs, all_auto_pairs):
        gold_counter = Counter( gold_pairs)
        auto_counter = Counter( auto_pairs)
        comm_counter = gold_counter & auto_counter

        gold_count += sum( gold_counter.values())
        auto_count += sum( auto_counter.values())
        comm_count += sum( comm_counter.values())

        #precision = None if auto_count == 0 else comm_count / auto_count
        #recall = None if gold_count == 0 else comm_count / gold_count
        #f1_score = None if precision is None or recall is None else \
        #        2 * precision * recall / ( precision + recall )
    print( gold_count, auto_count, comm_count)
    precision = comm_count / auto_count
    recall = comm_count / gold_count
    print( "Precision:", round( 100 * precision, 1))
    print( "Recall:   ", round( 100 * recall, 1))
    f1_score = 2 * precision * recall / ( precision + recall )
    print( "F1 score: ", round( 100 * f1_score, 1))


def perform_test( gold_file_name, auto_file_name):
    gold_pairs = process_input( gold_file_name, 0, ' ')
    auto_pairs = process_input( auto_file_name, 5, '|')
    compare_pairs( gold_pairs, auto_pairs)

if __name__ == "__main__":
    gold_file_name = sys.argv[ 1 ]
    auto_file_name = sys.argv[ 2 ]

    #gold_file_name = "../data/test_results/gold_"+corp_name+"_"+sample_num
    #auto_file_name = "../data/test_results/"+corp_name+"_"+run_num+"_"+sample_num
    perform_test( gold_file_name, auto_file_name)
    #print( "FA")
    #perform_test( "../data/test_results/gold_test_cssk_out", "../data/test_results/cssk_0_test_300_out")
    #print( "UD")
    #perform_test( "../data/test_results/gold_test_csen_out", "../data/test_results/csen_2_test_300_out")
    #print( "FAUD")
    #perform_test( "../data/test_results/gold_test_cssk_out", "../data/test_results/cssk_3_test_300_out")
    #print( "SIM")
    #perform_test( "../data/test_results/gold_test_200_out", "../data/test_results/sim_test_200_out_3")



