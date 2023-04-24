import sys
import os

def perform_test( gold_name, auto_name):
    #print( os.getcwd())
    with open( gold_name) as gold_file, open( auto_name) as auto_file:
        gold_records = {}
        for gold_line in gold_file:
            lemma, ordnum, sent, lemma2, args, sent_args = gold_line.rstrip().split( '\t')
            key = lemma + '|' + ordnum + '|' + sent
            gold_val = ( lemma2,  args, sent_args )
            gold_records[ key ] = gold_val

        pos = 0
        verb_neg = 0
        arg_neg = 0
        for aut_line in auto_file:
            lemma, ordnum, sent, lemma2, args, sent_args = aut_line.rstrip().split( '\t')
            key = lemma + '|' + ordnum + '|' + sent
            auto_val = ( lemma2,  args, sent_args )
            if key in gold_records:
                #if gold_records[ key ] == None:
                #    print( key)
                gold_val = gold_records[ key ]
                #gold_records[ key ] = None
                if gold_val == auto_val:
                    pos += 1
                elif gold_val[ 0 ] != auto_val[ 0 ] and gold_val[ 1: ] == auto_val[ 1: ]:
                    verb_neg += 1
                else:
                    arg_neg += 1

        not_found = 100 - pos - verb_neg - arg_neg
        print( pos, verb_neg, arg_neg, not_found)

if len( sys.argv) == 3:
    gold_name = sys.argv[ 1 ]
    auto_name = sys.argv[ 2 ]
    perform_test( gold_name, auto_name)