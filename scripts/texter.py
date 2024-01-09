import sys
import pickle

class Texter:
    def __init__( self):
        self.output = sys.stdout

    def write_dict( self, valency_dict, out_name, is_bilignual):
        with open( out_name, 'w') as output:
            self.output = output
            verb_lemmas = sorted( valency_dict.keys())
            for verb_lemma in verb_lemmas:
                self.printout( "========================================")
                verb_record = valency_dict[ verb_lemma ]
                verb_insts = sum( [ len( frame_type.insts)
                                    for frame_type in verb_record.frame_types ])
                self.printout( verb_lemma + "  [" + str( len( verb_record.frame_types))
                       + " frames] (" + str( verb_insts) + " occurs)")
                indent_num = 0
                for frame_type in verb_record.subframes:
                    self.print_frame_by_tree( frame_type, indent_num, is_bilignual)

    def print_examples( self, frame_type, indent_num, is_bilignual):
        for j, frame_inst in enumerate( frame_type.insts):
            token_forms = [ str( token) for token in frame_inst.sent_tokens ]
            elided_token_forms = [ '[' + str( token) + ']'
                                   for token in frame_inst.elided_tokens ]
            exam_sent = ' '.join( token_forms + elided_token_forms)
            example_indent = indent_num * '\t' + "\t\t\t"
            self.printout( example_indent + str( j+1) + ")  " + exam_sent)
            if is_bilignual and frame_inst.link is not None:
                frame_inst_link = frame_inst.link
                other_frame_inst = frame_inst_link.get_other_frame_inst( frame_inst)
                other_frame_type = other_frame_inst.type
                other_verb = other_frame_type.verb_lemma
                other_args = "   ".join( [ str( arg) for arg in other_frame_type.args ])
                other_type_str = other_verb + "  :  " + other_args
                self.printout( example_indent + '\t' + other_type_str)

                token_forms = [ str( token) for token in other_frame_inst.sent_tokens ]
                elided_token_forms = [ '[' + str( token) + ']'
                                       for token in other_frame_inst.elided_tokens ]
                exam_sent = ' '.join( token_forms + elided_token_forms)
                self.printout( example_indent + "\t\t" + exam_sent)

    def print_frame( self, frame_type, indent_num, is_bilignual):
        index = frame_type.tree_index
        index_part = '\t' + str( index) + "]" + '\t'
        indent = indent_num * '\t'

        argnum_part = str( len( frame_type.args)) + " args ("
        super_part = "  [" + ';'.join( [ str( superframe.tree_index) for
                     superframe in frame_type.superframes ]) + ']'
        if frame_type.superframes == []:
            super_part = ""
        occurnum_part = str( len( frame_type.insts)) + " occurs)"
        pre_frame_string = "\t\t" + indent
        frame_string = "   ".join( [ str( arg) for arg in frame_type.args ])
        self.printout( index_part + indent + argnum_part + occurnum_part + super_part)
        self.printout( pre_frame_string + frame_string)
        self.print_examples( frame_type, indent_num, is_bilignual)

    def print_frame_by_tree( self, frame_type, indent_num, is_bilignual):
        self.print_frame( frame_type, indent_num, is_bilignual)
        for subframe in frame_type.subframes:
            if frame_type.tree_index < subframe.tree_index:
                self.print_frame_by_tree( subframe, indent_num+1, is_bilignual)

    def printout( self, string):
        print( string, file=self.output)


if __name__ == "__main__":
    if len( sys.argv) == 4:
        dict_filename = sys.argv[ 1 ]
        output_form = sys.argv[ 2 ]
        output_name = sys.argv[ 3 ]

        valency_dict = pickle.load( open( dict_filename, "rb" ))
        Texter.write_dict( valency_dict, output_name)

