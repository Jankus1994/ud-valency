from copy import copy, deepcopy
from collections import defaultdict

class Obl_handling_record:
    def __init__( self, obl_frame_type_arg, obl_frame_type, reduced_frame_type,
                  obl_ratio_limit, min_obl_inst_num):
        self.obl_frame_type_arg = obl_frame_type_arg
        self.obl_form_str = self.obl_frame_type_arg.to_string().lstrip( "obl-")
        self.obl_token_forms = self.get_token_forms()
        self.obl_frame_type = obl_frame_type
        self.obl_frame_lemma = self.obl_frame_type.verb_lemma
        self.reduced_frame_type = reduced_frame_type
        self.obl_insts_num = len( self.obl_frame_type.insts)
        self.reduced_insts_num = 0
        if self.reduced_frame_type is not None:
            self.reduced_insts_num = len( self.reduced_frame_type.insts)
        self.total_insts_num = self.obl_insts_num + self.reduced_insts_num
        self.obl_ratio = round( self.obl_insts_num / self.total_insts_num, 3)

        self.should_be_included = True
        if self.obl_ratio < obl_ratio_limit or \
                self.obl_insts_num < min_obl_inst_num:
            self.should_be_included = False

    def get_token_forms( self):
        token_forms = []
        for inst in self.obl_frame_type_arg.insts:
            token_form = inst.token.get_form()
            token_form += '-' + self.obl_form_str
            token_forms.append( token_form)
        return token_forms


class Record_counter:
    def __init__( self, name):
        self.name = name
        self.record_dict = defaultdict( list)
    def add_record( self, key, record):
        self.record_dict[ key ].append( record)

    def print_dict( self):
        print_dict = {}
        for freq, record_list in self.record_dict.items():
            incl_record_list = [ obl_record for obl_record in record_list
                                 if obl_record.should_be_included ]
            record_count = len( record_list)
            incl_record_count = len( incl_record_list)
            print_value = record_count #str( record_count) + '/' + str( incl_record_count)
            print_dict[ freq ] = print_value

        print( self.name)
        #print( sorted( print_dict.items()))
        for key, value in sorted( print_dict.items()):
            print( key, value, sep='\t')


class Obl_stats_handler:
    def __init__( self, obl_ratio_limit):
        self.obl_ratio_limit = obl_ratio_limit

        self.obl_inst_counter = Record_counter( "obl_inst")
            # obl frame types with x insts
        self.tot_inst_counter = Record_counter( "tot_inst")
            # obl frame types with x insts and y insts + reduced insts
        self.red_inst_counter = Record_counter( "red_inst")
            # obl frame types with x insts in corresponding reduced frame
        self.ratio_counter = Record_counter( "ratio_counter")
            # obl frame types with obl ratio x
        self.arg_counter = Record_counter( "arg")
            # obl frame types with x args
        self.arg_deprel_counter = Record_counter( "arg_deprel")
            # obl frame type arg deprels with x occurences

        self.record_counters = [ self.obl_inst_counter,
                                 #self.tot_inst_counter,
                                 #self.red_inst_counter,
                                 #self.ratio_counter,
                                 #self.arg_counter,
                                 #self.arg_deprel_counter
                               ]

    def process_obl_record( self, obl_record):
        obl_insts_num = obl_record.obl_insts_num
        total_insts_num = obl_record.total_insts_num
        red_insts_num = obl_record.reduced_insts_num
        obl_ratio = obl_record.obl_ratio
        self.obl_inst_counter.add_record( obl_insts_num, obl_record)
        #self.tot_inst_counter.add_record( ( obl_insts_num, total_insts_num ),
        #                                  obl_record)
        self.red_inst_counter.add_record( red_insts_num, obl_record)
        self.tot_inst_counter.add_record( total_insts_num, obl_record)
        self.ratio_counter.add_record( obl_ratio, obl_record)

        # frame examining stats
        frame_type_args = obl_record.obl_frame_type.args
        arg_num = len( frame_type_args)
        self.arg_counter.add_record( arg_num, obl_record)
        #if obl_ratio >= self.obl_ratio_limit:
        #    self.incl_arg_num_counter[ arg_num ] += 1
        for arg in frame_type_args:
            self.arg_deprel_counter.add_record( arg.deprel, obl_record)
            #if obl_ratio >= self.obl_ratio_limit:
            #    self.incl_arg_deprels_counter[ arg.deprel ] += 1

    def print_stats( self):
        for record_counter in self.record_counters:
            record_counter.print_dict()
            print( "")



class Extraction_finalizer:
    def __init__( self, dict_of_verbs, obl_ratio_limit, min_obl_inst_num,
                  lang_mark):
        self.dict_of_verbs = dict_of_verbs
        self.obl_ratio_limit = obl_ratio_limit
        self.min_obl_inst_num = min_obl_inst_num
        self.obl_args = []
        #self.def_obl_dict = defaultdict( int)
        self.lang_mark = lang_mark

    def add_obl_arg( self, obl_frame_type_arg):
        """ called from Frame_type._control_obl """
        self.obl_args.append( obl_frame_type_arg)

    def finalize_extraction( self):
        self.obl_handling()

    def examine_token_frequency( self, obl_handling_records):
        token_form_set_dict = defaultdict( set)
        for obl_record in obl_handling_records:
            verb_lemma = obl_record.obl_frame_lemma
            # only cases and prepositions
            obl_form_str = obl_record.obl_form_str
            token_form_set_dict[ obl_form_str ].add( verb_lemma)
            # including token forms
            #token_forms = obl_record.obl_token_forms
            #for token_form in token_forms:
            #    token_form_set_dict[ token_form ].add( verb_lemma)
            #
        token_form_counter = {}
        for token_form, verb_lemma_set in token_form_set_dict.items():
            token_form_counter[ token_form ] = len( verb_lemma_set)
        sort_token_form_counter = self.counter_sort( token_form_counter)
        #
        #for token_form, verb_count in sort_token_form_counter:
        #    print( verb_count, token_form)
        #return
        count_counter = defaultdict( int)
        for token_form, verb_count in sort_token_form_counter:
            count_counter[ verb_count ] += 1
        sort_count_counter = self.counter_sort( count_counter)
        for verb_count, freq in sort_count_counter:
            print( freq, verb_count)



    def obl_handling( self):
        obl_handling_records = []
        obl_stats_handler = Obl_stats_handler( self.obl_ratio_limit)
        for obl_frame_type_arg in self.obl_args:
            obl_frame_type = obl_frame_type_arg.frame_type

            verb_lemma = obl_frame_type.verb_lemma
            verb_record = self.dict_of_verbs[ verb_lemma ]

            # searching reduced frame in the verb record
            copy_obl_frame_type = copy( obl_frame_type)
            copy_obl_frame_type.args = copy( obl_frame_type.args)
            copy_obl_frame_type.remove_arg(obl_frame_type_arg)
            reduced_frame_type = verb_record.find_frame_type( copy_obl_frame_type)


            obl_handling_record = Obl_handling_record( obl_frame_type_arg,
                                    obl_frame_type, reduced_frame_type,
                                    self.obl_ratio_limit, self.min_obl_inst_num)

            obl_handling_records.append( obl_handling_record)
            obl_stats_handler.process_obl_record( obl_handling_record)



        # print( self.obl_ratio_limit, self.lang_mark)
        # for arg_num in sorted( frame_arg_num_counter.keys()):
        #     tot_count = frame_arg_num_counter[ arg_num ]
        #     incl_count = incl_arg_num_counter[ arg_num ]
        #     print( arg_num, tot_count, incl_count)
        # for deprel in sorted( frame_arg_deprels_counter.keys()):
        #     tot_count = frame_arg_deprels_counter[ deprel ]
        #     incl_count = incl_arg_deprels_counter[ deprel ]
        #     print( deprel, tot_count, incl_count)
        # #print( sorted( frame_arg_num_counter.items()))
        # #print( self.counter_sort( frame_arg_deprels_counter))
        # print( "")
        # return

        #self.examine_token_frequency( obl_handling_records)
        #return

        # printing ratio a inst count stats
        #print( self.min_obl_inst_num)
        obl_stats_handler.print_stats()
        return

        # printing most frequent form of obl arg
        obl_form_counter = defaultdict( int)
        for obl_handling_record in obl_handling_records:
            obl_form = obl_handling_record.obl_form_str
            obl_form_counter[ obl_form ] += 1
        sort_obl_form_counter = self.counter_sort( obl_form_counter)
        most_freq_form_counter = { key: value for key, value
                in sort_obl_form_counter if value > 10 }
        for key, value in most_freq_form_counter.items():
            print( key, value, sep='\t')




    @staticmethod
    def counter_sort( counter_dict):
        return sorted( counter_dict.items(), key=lambda item: item[1], reverse=True)

