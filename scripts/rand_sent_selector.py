from random import sample
import sys

#all_sent_num = 940427  # cs-sk
#all_sent_num = 964152  # cs-en
corp_name = sys.argv[ 1 ]  # acquis_cs_en / acquis_cs_sk
test_corp_name = sys.argv[ 2 ]  # acquis_cs_en_test / acquis_cs_sk_test
sample_id = sys.argv[ 3 ]  # eg. 1 2 3 12 13 23 123

#sample_num = 1000
# chosen_sent_ids = sample( range( all_sent_num), sample_num)

treebank_name = "../data/b_conllu/"+corp_name+".conllu"
sent_ids_name = "../data/test_results/"+corp_name+"_test_ids"
output_name = "../data/b_conllu/"+test_corp_name+"_"+sample_id+".conllu"
align_file_name = "../data/b_aligned/"+corp_name
out_align_name = "../data/b_aligned/"+test_corp_name+"_"+sample_id
gold_input_name = "../data/test_results/gold_"+test_corp_name
gold_output_name = "../data/test_results/gold_"+test_corp_name+"_"+sample_id

# with open( sent_ids_name, 'w') as sent_ids_file:
#     for i in range( all_sent_num):
#         if i in chosen_sent_ids:
#             print( i, file=sent_ids_file)



with open( treebank_name, 'r') as input_file, \
        open( sent_ids_name, 'r') as sent_ids_file, \
        open( output_name, 'w') as output_file, \
        open( align_file_name, 'r') as align_file, \
        open( out_align_name, 'w') as out_align_file, \
        open( gold_input_name, 'r') as gold_input, \
        open( gold_output_name, 'w') as gold_output:

    sent_ids = []
    for line in sent_ids_file:
        sent_id = int( line.rstrip( '\n'))
        sent_ids.append( sent_id)

    my_indices = []
    if '1' in sample_id:
        my_indices += list( range( 0, 100))
    if '2' in sample_id:
        my_indices += list( range( 100, 200))
    if '3' in sample_id:
        my_indices += list( range( 200, 300))

    my_sent_ids = [ sent_ids[ index ] for index in range( len( sent_ids))
                    if index in my_indices ]

    sent_permitted = False
    beginning = True
    for line in input_file:
        line = line.rstrip( '\n')
        if line == "" or line.startswith( "#"):
            sent_permitted = False
        if line.startswith( "# sent_id = "):
            sent_id = line.lstrip( "# sent_id = ")[ :-3 ]
            if int( sent_id) in my_sent_ids: #chosen_sent_ids:
                sent_permitted = True
                if not beginning:
                    print( "", file=output_file)
                else:
                    beginning = False
        if sent_permitted:
            print( line, file=output_file)

    for index, line, in enumerate( align_file):
        if index in sent_ids:
            print( line.rstrip( '\n'), file=out_align_file)

    for index, line, in enumerate( gold_input):
        if index in my_indices:
            print( line.rstrip( '\n'), file=gold_output)
