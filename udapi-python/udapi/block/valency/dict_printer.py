import sys
import pickle
from collections import Counter

class Dict_printer:

    @staticmethod
    def print_dict( output_form, dict_of_verbs, output_name, other_dict=None):
        is_bilignual = other_dict is not None
        if output_form == "stats":
            Dict_printer.print_stats( dict_of_verbs, is_bilignual,
                                           out_name=output_name)
        # elif output_form == "text":
        #     Dict_printer.print_mono_frames( dict_of_verbs,
        #                                     out_name=output_name)
        elif output_form == "text":
            Dict_printer.print_frames_by_tree( dict_of_verbs, is_bilignual,
                                            out_name=output_name)
        # elif output_form == "textw":
        #     Dict_printer.print_mono_frames( dict_of_verbs, with_examples=False,
        #                                     out_name=output_name)
        elif output_form == "textw":
            Dict_printer.print_frames_by_tree( dict_of_verbs, is_bilignual,
                                              with_examples=False,
                                              out_name=output_name)
        elif output_form == "bin":
            output_object = dict_of_verbs
            if other_dict is not None:
                output_object = ( dict_of_verbs, other_dict )
            pickle.dump( output_object, open( output_name, 'wb'))

        elif output_form == "test":
            Dict_printer.print_test_sample( dict_of_verbs, output_name)

    @staticmethod
    def print_verb_pairs( a_b_valency_dict):
        print( len( a_b_valency_dict.keys()))
        for a_verb_lemma in a_b_valency_dict.keys():
            print( a_verb_lemma)
            a_verb_record = a_b_valency_dict[ a_verb_lemma ]
            for a_frame_type in a_verb_record.frame_types:
                for a_b_ft_link in a_frame_type.links:
                    b_frame_type = a_b_ft_link.get_other_frame_type(a_frame_type)
                    b_verb_lemma = b_frame_type.verb_lemma
                    print( '\t', a_verb_lemma, b_verb_lemma)

    @staticmethod
    def print_mono_frames( dict_of_verbs, with_examples=True, out_name=""):
        if out_name:
            output = open( out_name, 'w')
        else:
            output = sys.stdout

        verb_lemmas = sorted( dict_of_verbs.keys())
        for verb_lemma in verb_lemmas:
            print( "========================================", file=output)
            verb_record = dict_of_verbs[ verb_lemma ]
            verb_insts = sum( [ len( frame_type.insts)
                                for frame_type in verb_record.frame_types ])
            print( verb_lemma, "  [" + str( len( verb_record.frame_types))
                   + " frames] (" + str( verb_insts) + " occurs)", file=output)
            for i, frame_type in enumerate( verb_record.frame_types):
                index = i + 1
                indent_num = 0
                Dict_printer.print_frame(
                        frame_type, index, indent_num, output, with_examples)
        if out_name:
            output.close()

    @staticmethod
    def print_frames_by_tree( dict_of_verbs, is_bilignual, with_examples=True, out_name=""):
        if out_name:
            output = open( out_name, 'w')
        else:
            output = sys.stdout

        verb_lemmas = sorted( dict_of_verbs.keys())
        for verb_lemma in verb_lemmas:
            print( "========================================", file=output)
            verb_record = dict_of_verbs[ verb_lemma ]
            verb_insts = sum( [ len( frame_type.insts)
                                for frame_type in verb_record.frame_types ])
            print( verb_lemma, "  [" + str( len( verb_record.frame_types))
                   + " frames] (" + str( verb_insts) + " occurs)", file=output)
            indent_num = 0
            for frame_type in verb_record.subframes:
                Dict_printer.print_frame_by_tree(
                        frame_type, indent_num, output,
                        with_examples, is_bilignual)
        if out_name:
            output.close()

    @staticmethod
    def print_examples( frame_type, indent_num, output, is_bilignual):
        for j, frame_inst in enumerate( frame_type.insts):
            token_forms = [ str( token) for token in frame_inst.sent_tokens ]
            elided_token_forms = [ '[' + str( token) + ']'
                                   for token in frame_inst.elided_tokens ]
            exam_sent = ' '.join( token_forms + elided_token_forms)
            example_indent = indent_num * '\t' + "\t\t\t"
            print( example_indent + str( j+1) + ")  " +
                   exam_sent, file=output)
            if is_bilignual and frame_inst.link is not None:
                frame_inst_link = frame_inst.link
                other_frame_inst = frame_inst_link.get_other_frame_inst( frame_inst)
                other_frame_type = other_frame_inst.type
                other_verb = other_frame_type.verb_lemma
                other_args = "   ".join( [ str( arg) for arg in other_frame_type.args ])
                other_type_str = other_verb + "  :  " + other_args
                print( example_indent + '\t' + other_type_str, file=output)

                token_forms = [ str( token) for token in other_frame_inst.sent_tokens ]
                elided_token_forms = [ '[' + str( token) + ']'
                                       for token in other_frame_inst.elided_tokens ]
                exam_sent = ' '.join( token_forms + elided_token_forms)
                print( example_indent + "\t\t" + exam_sent, file=output)

    @staticmethod
    def print_frame( frame_type, indent_num, output,
                     with_examples, is_bilignual):
        index = frame_type.tree_index
        index_part = '\t' + str( index) + "]" + '\t'
        indent = indent_num * '\t'
        #print( indent + index_part, file=output)
        #return
        argnum_part = str( len( frame_type.args)) + " args ("
        super_part = "  [" + ';'.join( [ str( superframe.tree_index) for
                     superframe in frame_type.superframes ]) + ']'
        if frame_type.superframes == []:
            super_part = ""
        if with_examples:
            occurnum_part = str( len( frame_type.insts)) + " occurs)"
            pre_frame_string = "\t\t" + indent
            frame_string = "   ".join( [ str( arg) for arg in frame_type.args ])
        else:
            occurnum_part = str( len( frame_type.insts)) + ')'
            pre_frame_string = "\t\t\t" + indent
            frame_string = "   ".join( [ arg.to_str() for arg in frame_type.args ])
        print( index_part + indent + argnum_part + occurnum_part + super_part,
               file=output)
        print( pre_frame_string + frame_string, file=output)
        if with_examples:
            Dict_printer.print_examples( frame_type, indent_num, output, is_bilignual)


    @staticmethod
    def print_frame_by_tree( frame_type, indent_num, output,
                             with_examples, is_bilignual):
        Dict_printer.print_frame(frame_type, indent_num,
                                 output, with_examples, is_bilignual)
        for subframe in frame_type.subframes:
            if frame_type.tree_index < subframe.tree_index:
                Dict_printer.print_frame_by_tree(
                        subframe, indent_num+1, output,
                        with_examples, is_bilignual)
        return

    @staticmethod
    def print_test_sample( dict_of_verbs, out_name):
        output = open( out_name, 'w')
        verb_lemmas = sorted( dict_of_verbs.keys())
        for verb_lemma in verb_lemmas:
            verb_record = dict_of_verbs[ verb_lemma ]
            for frame_type in verb_record.frame_types:
                args = ' '.join( [ str( arg) for arg in frame_type.args])
                for frame_inst in frame_type.insts:
                    ordnum = -1
                    for token in frame_inst.sent_tokens:
                        if token.is_frame_predicate():
                            ordnum = token.ord
                    sent = ' '.join( [ token.form for token in frame_inst.sent_tokens ])
                    token_forms = [ str( token) for token in frame_inst.sent_tokens ]
                    elided_token_forms = [ '[' + str( token) + ']'
                                           for token in frame_inst.elided_tokens ]
                    exam_sent = ' '.join( token_forms + elided_token_forms)
                    print( verb_lemma, ordnum, sent, verb_lemma, args, exam_sent, sep='\t', file=output)

    @staticmethod
    def print_verbs_by_arg_form( dict_of_verbs, arg_form):
        freq_dict = Counter()
        for verb_record in dict_of_verbs.values():
            insts_num = 0
            verb_conv = False
            for frame_type in verb_record.frame_types:
                for frame_arg in frame_type.args:
                    if arg_form in frame_arg.form and "expl" not in frame_arg.deprel:
                        verb_conv = True
                        break
                if verb_conv:
                    insts_num += len( frame_type.insts)
            freq_dict[ verb_record.lemma ] = insts_num
        most_common = freq_dict.most_common( 50)
        for item in most_common:
            print( item)

    @staticmethod
    def print_stats(dict_of_verbs, out_name=""):
        if out_name:
            output = open( out_name, 'w')
        else:
            output = sys.stdout

        verb_lemmas = sorted( dict_of_verbs.keys())
        frames_sum = 0
        args_sum = 0
        arg_insts_sum = 0
        args_per_frame_sum = 0
        insts_sum = 0
        insts_per_frame_sum = 0
        for verb_lemma in verb_lemmas:
            verb_record = dict_of_verbs[ verb_lemma ]
            frames_sum += len( verb_record.frame_types)
            partial_args_sum = 0
            partial_insts_sum = 0
            for frame_type in verb_record.frame_types:
                partial_args_sum += len( frame_type.args)
                partial_insts_sum += len( frame_type.insts)
                arg_insts = len( frame_type.args) * len( frame_type.insts)
                #assert arg_insts == sum( len( frame_type_arg.insts) \
                #        for frame_type_arg in frame_type.args)
                #assert arg_insts == sum( len( frame_inst.args) \
                #        for frame_inst in frame_type.insts)
                arg_insts_sum += arg_insts
            args_sum += partial_args_sum
            try:
                args_per_frame = partial_args_sum / len( verb_record.frame_types)
                args_per_frame_sum += args_per_frame

                insts_sum += partial_insts_sum
                insts_per_frame = partial_insts_sum / len( verb_record.frame_types)
                insts_per_frame_sum += insts_per_frame
            except ZeroDivisionError:
                pass

        frames_per_verb_mean = round( frames_sum / len( verb_lemmas), 3)
        args_per_frame_mean_1 = round( args_sum / frames_sum, 3)
        args_per_frame_mean_2 = round( args_per_frame_sum / len( verb_lemmas), 3)
        insts_per_verb_mean = round( insts_sum / len( verb_lemmas), 3)
        insts_per_frame_mean_1 = round( insts_sum / frames_sum, 3)
        insts_per_frame_mean_2 = round( insts_per_frame_sum / len( verb_lemmas), 3)

        print( "V    :", len( verb_lemmas), file=output)
        print( "F    :", frames_sum, file=output)
        print( "I    :", insts_sum, file=output)
        print( "A    :", args_sum, file=output)
        print( "AI   :", arg_insts_sum, file=output)
        print( "F/V  :", frames_per_verb_mean, file=output)
        print( "A/F 1:", args_per_frame_mean_1, file=output)
        print( "A/F 2:", args_per_frame_mean_2, file=output)
        print( "I/V  :", insts_per_verb_mean, file=output)
        print( "I/F 1:", insts_per_frame_mean_1, file=output)
        print( "I/F 2:", insts_per_frame_mean_2, file=output)

if __name__ == "__main__":
    if len( sys.argv) == 4:
        dict_filename = sys.argv[ 1 ]
        output_form = sys.argv[ 2 ]
        output_name = sys.argv[ 3 ]

        dict_of_verbs = pickle.load( open( dict_filename, "rb" ))
        Dict_printer.print_dict( output_form, dict_of_verbs, output_name)

