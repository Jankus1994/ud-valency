from distance_measurer import *
from ud_corpus_reader import extract_verb_lemmas
import pickle
import datetime
from random import sample, seed

def read_treebanks():
    treebanks_location = "C:/Users/farya/diplomka/ud-valency/valency/data/ud-treebanks-v2.3/"
    cs_corpus_name = treebanks_location + "UD_Czech-PDT/cs_pdt-ud-train.conllu"
    sk_corpus_name = treebanks_location + "UD_Slovak-SNK/sk_snk-ud-train.conllu"
    cs_verb_dict = extract_verb_lemmas( cs_corpus_name)
    sk_verb_dict = extract_verb_lemmas( sk_corpus_name)
    print( len( cs_verb_dict))  # 5161
    print( len( sk_verb_dict))  # 2326

    cs_verb_dict_s = dict( sorted( cs_verb_dict.items(), key=lambda item: item[1], reverse=True))
    sk_verb_dict_s = dict( sorted( sk_verb_dict.items(), key=lambda item: item[1], reverse=True))

    verb_dicts = cs_verb_dict_s, sk_verb_dict_s
    with open( "verb_lists.pickle", 'wb') as verb_out_file:
        pickle.dump( verb_dicts, verb_out_file)

def choose_lemmas():
    with open( "verb_lists.pickle", 'rb') as verb_in_file:
        verb_dicts = pickle.load( verb_in_file)
        cs_verb_dict_s, sk_verb_dict_s = verb_dicts

        cs_all_lemmas = list( cs_verb_dict_s.keys())
        sk_all_lemmas = list( sk_verb_dict_s.keys())

        cs_most_freqs_verbs = cs_all_lemmas[ :200 ]
        sk_most_freqs_verbs = sk_all_lemmas[ :200 ]

        cs_all_rand_verbs = sample( cs_all_lemmas, 200)
        sk_all_rand_verbs = sample( sk_all_lemmas, 200)

        cs_most_freqs_verbs = list( cs_verb_dict_s.keys())[ :200 ]
        sk_most_freqs_verbs = list( sk_verb_dict_s.keys())[ :200 ]

        #output_lemmas( "cs_all_lemmas.txt", list( cs_verb_dict_s.keys()))
        #output_lemmas( "sk_all_lemmas.txt", list( sk_verb_dict_s.keys()))
        #output_lemmas( "cs_rand_lemmas.txt", cs_all_rand_verbs[ :100 ])
        #output_lemmas( "sk_rand_lemmas.txt", sk_all_rand_verbs[ :100 ])
        #output_lemmas( "cs_rand_lemmas_ext.txt", cs_all_rand_verbs)
        #output_lemmas( "sk_rand_lemmas_ext.txt", sk_all_rand_verbs)
        output_lemmas( "cs_freq_lemmas.txt", cs_most_freqs_verbs, cs_verb_dict_s)
        output_lemmas( "sk_freq_lemmas.txt", sk_most_freqs_verbs, sk_verb_dict_s)

def output_lemmas( filename, lemmas_list, freq_dict=None):
        with open( filename, 'w', encoding="utf-8") as output_freq_file:
            if freq_dict is not None:
                for verb_lemma in lemmas_list:
                    print( verb_lemma, freq_dict[ verb_lemma ], file=output_freq_file)
            else:
                for verb_lemma in lemmas_list:
                    print( verb_lemma, file=output_freq_file)

def load_testing( filename, verb_dict):
    with open( filename, 'r', encoding="utf-8") as input_file:
        lemma_dict = {}
        a_verb_list = []

        for line in input_file:
            a_lemma, b_lemmas_str = line.rstrip( '\n').split( '\t')
            a_verb_list.append( a_lemma)
            if b_lemmas_str == "XXX":  # wrong a-lemma
                lemma_dict[ a_lemma ] = None
            else:
                b_lemmas_list = b_lemmas_str.split( " / ")
                is_present = False
                for b_lemma in b_lemmas_list:
                    if b_lemma in verb_dict:
                        is_present = True
                        break
                lemma_dict[ a_lemma ] = ( is_present, b_lemmas_list )
        return a_verb_list, lemma_dict

def testing( test_out_name, allow_substitutions=True, allow_specific=True):
    with open( "verb_lists.pickle", 'rb') as verb_in_file, open( test_out_name, 'w') as out:
        print( datetime.datetime.now())#, file=out)
        verb_dicts = pickle.load( verb_in_file)
        cs_verb_fdict_s, sk_verb_fdict_s = verb_dicts

        cs_rand_list, cs_sk_rand_dict = load_testing( "cs_sk_rand.txt", sk_verb_fdict_s)
        match_and_test( cs_rand_list, sk_verb_fdict_s.keys(), cs_sk_rand_dict, out)
        sk_rand_list, sk_cs_rand_dict = load_testing( "sk_cs_rand.txt", cs_verb_fdict_s)
        match_and_test( sk_rand_list, cs_verb_fdict_s.keys(), sk_cs_rand_dict, out, reverse=True)
        cs_freq_list, cs_sk_freq_dict = load_testing( "cs_sk_freq.txt", sk_verb_fdict_s)
        match_and_test( cs_freq_list, sk_verb_fdict_s.keys(), cs_sk_freq_dict, out)
        match_and_test( cs_freq_list[ :100 ], sk_verb_fdict_s.keys(), cs_sk_freq_dict, out)
        sk_freq_list, sk_cs_freq_dict = load_testing( "sk_cs_freq.txt", cs_verb_fdict_s)
        match_and_test( sk_freq_list, cs_verb_fdict_s.keys(), sk_cs_freq_dict, out, reverse=True)
        match_and_test( sk_freq_list[ :100 ], cs_verb_fdict_s.keys(), sk_cs_freq_dict, out, reverse=True)
        print( datetime.datetime.now(), file=out)


def match_and_test(a_verbs, b_verbs, a_b_result_dict, out, reverse=False, allow_substitutions=True, allow_specific=True):
    if allow_specific:
        measurer = Cs_Sk_distance_measurer( allow_substitution=allow_substitutions)
    else:
        measurer = General_measurer( allow_substitution=allow_substitutions)
    ok_input_count = 0
    present_res_count = 0
    correct_res_count = 0
    uniq_correct_res_count = 0
    weight_correct_res_count = 0
    min_dist_sum = 0
    thresholds = [ 0 ] * 5
    j = 0
    time_before = datetime.datetime.now()
    for a_verb in a_verbs:
        j += 1
        min_distance, closest_b_verbs = measurer.find_closest_verbs( a_verb, b_verbs, out, reverse=reverse)

        correct_results = a_b_result_dict[ a_verb ]
        if correct_results is not None:
            ok_input_count += 1
            is_present, correct_verbs = correct_results
            if is_present:
                present_res_count += 1
                intersection = set( correct_verbs) & set( closest_b_verbs)
                least_one = bool( intersection)
                precision = len( intersection) / len( closest_b_verbs)
                min_dist_sum += min_distance
                result_line = '\t'.join( [ a_verb, str( least_one), str( precision), str( min_distance),
                                           str( correct_results), str( closest_b_verbs)])
                for i in range( len( thresholds)):
                    if min_distance <= i and least_one:
                        thresholds[ i ] += 1
                correct_res_count += least_one
                weight_correct_res_count += precision
                if precision == 1:
                    uniq_correct_res_count += 1
        #print( j, a_verb, min_distance, closest_b_verbs)#, file=out)

    weight_correct_res_perc = 100 / present_res_count * weight_correct_res_count
    time_complete = datetime.datetime.now() - time_before
    print( time_complete)

    print( ok_input_count, present_res_count, correct_res_count, weight_correct_res_perc, \
           uniq_correct_res_count, thresholds)#, file=out)
    print( "===========", file=out)


seed( 2000)
#read_treebanks()
#choose_lemmas()
#match_similars()
#testing( "test_out_general.txt")
#testing( "test_out_specific.txt")
testing( "gener_direct_out.txt", allow_substitutions=True, allow_specific=False)
testing( "gener_direct_out.txt", allow_substitutions=False, allow_specific=False)
testing( "gener_direct_out.txt", allow_substitutions=True, allow_specific=True)