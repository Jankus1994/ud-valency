import sys, pickle
from yattag import *  # yattag trick: "klass" will be replaced with "class"
from collections import Counter

from htmler_mono import HTMLer_mono

def character_sort_key( char, alphabet):
    if char in alphabet:
        return alphabet.index( char)
    return len( alphabet) + ord( char)

def english_sort_key( word):
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    return [ character_sort_key( char, alphabet) for char in word.lower() ]

def czech_sort_key( word):
    word = word.replace("ch", "ŭ")
    alphabet = list("aábcčdďeéěfghŭiíjklmnňoópqrřsštťuúůvwxyýzž")
    return [ character_sort_key( char, alphabet) for char in word.lower() ]

def slovak_sort_key( word):
    word = word.replace("ch", "ŭ")
    word = word.replace("dz", "ÿ")
    word = word.replace("dž", "ç")
    alphabet = list("aáäbcčdďÿçeéfghŭiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž")
    return [ character_sort_key( char, alphabet) for char in word.lower() ]

CUSTOM_SORT_KEYS = {
    "en": english_sort_key,
    "cs": czech_sort_key,
    "sk": slovak_sort_key
}

class HTMLer:
    def __init__( self):
        # self.column_names = [ "SHOW", "", "ARGUMENTS", "TRANS LEMMA", \
        #                  "", "TRANS ARGS", "STATS" ]
        self.colnum = 4
        self.dict_of_verbs = None
        self.list_of_lemmas = None
        self.a_frames_list = None
        self.a_lang_mark = ""
        self.b_lang_mark = ""
        
        self.doc, self.tag, self.text = Doc().tagtext()

    def create_html( self, dict_of_verbs, output_file_name, a_lang_mark, b_lang_mark):
        """ main method for creating an HTML table
        with verb frames using yattag liberary
        """
        print( "Creating HTML...", file=sys.stderr)
        self.a_lang_mark = a_lang_mark
        self.b_lang_mark = b_lang_mark
        self.dict_of_verbs = dict_of_verbs
        #self.list_of_lemmas = sorted( self.dict_of_verbs.keys())
        self.doc.asis( "<!DOCTYPE html>")

        with self.tag( "html"):
            self.html_head()
            self.html_body()

        val = self.doc.getvalue()
        #ind = indent( val)
        with open( output_file_name, 'w') as output_file:
            output_file.write( val)#ind)
        print( "HTML created.", file=sys.stderr)

    def html_head( self):
        with self.tag( "head"):
            with self.tag( "title"):
                self.text( "Table of verb frames")
            with self.tag( "meta", charset="UTF-8"):
                pass
            with self.tag( "link", rel="stylesheet", href="output.css"):
                pass

            with self.tag( "style"):
                self.text( ".hidden{ display:none; }")
                self.text( ".shown{ display:table-row; }")
            with self.tag( "script", type="text/javascript", src="info_showing.js"):
                pass

    def html_body( self):
        with self.tag( "body"):
            with self.tag( "h1"):
                self.text( f"{self.a_lang_mark}-{self.b_lang_mark} valency dictionary")
            with self.tag( "table", klass="table", cellindent="2.0"):
                stats, a_verbs_list = self.compute_overall_stats()
                self.list_of_lemmas = sorted( [verb.lemma for verb in a_verbs_list],
                                              key=CUSTOM_SORT_KEYS[self.a_lang_mark])
                with self.tag( "tr"):
                    with self.tag( "td"):
                        self.text( f"{self.a_lang_mark} verbs: {stats['a_verbs_num']}")
                        self.doc.stag( "br")
                        self.text( f"{self.a_lang_mark} frames: {stats['a_frames_num']}")
                    with self.tag( "td"):
                        self.text( f"{self.b_lang_mark} verbs: {stats['b_verbs_num']}")
                        self.doc.stag( "br")
                        self.text( f"{self.b_lang_mark} frames: {stats['b_frames_num']}")
                with self.tag( "tr"):
                    with self.tag( "td", colspan=2):
                        self.text( f"Frame links: {stats['frame_links_num']}")
                        self.doc.stag( "br")
                        self.text( f"Examples: {stats['examples_num']}")
            self.doc.stag( "br")
            self.create_verb_table()

    def compute_overall_stats( self):
        stats = Counter()
        a_verbs_set, a_frames_set = set(), set()
        b_verbs_set, b_frames_set = set(), set()
        for a_verb_record in self.dict_of_verbs.values():
            a_verb_stats = Counter()
            aa_frames_set, a_b_verbs_set, a_b_frames_set = set(), set(), set()
            for a_frame_type in a_verb_record.frame_types:
                a_frame_stats = Counter()
                aa_b_verbs_set, aa_b_frames_set = set(), set()
                for frame_link in a_frame_type.links:
                    b_frame_type = frame_link.get_other_frame_type( a_frame_type)
                    b_verb_record = b_frame_type.verb_record

                    a_verbs_set.add( a_verb_record)
                    a_frames_set.add( a_frame_type)
                    b_verbs_set.add( b_verb_record)
                    b_frames_set.add( b_frame_type)
                    stats[ "frame_links_num" ] += 1
                    stats[ "examples_num" ] += len( frame_link.frame_inst_links)

                    aa_frames_set.add( a_frame_type)
                    a_b_verbs_set.add( b_verb_record)
                    a_b_frames_set.add( b_frame_type)
                    a_verb_stats[ "frame_links_num" ] += 1
                    a_verb_stats[ "examples_num" ] += len( frame_link.frame_inst_links)

                    aa_b_verbs_set.add( b_verb_record)
                    aa_b_frames_set.add( b_frame_type)
                    a_frame_stats[ "frame_links_num" ] += 1
                    a_frame_stats[ "examples_num" ] += len( frame_link.frame_inst_links)

                a_frame_stats[ "b_verbs_num" ] = len( aa_b_verbs_set)
                a_frame_stats[ "b_frames_num" ] = len( aa_b_frames_set)
                a_frame_type.stats = a_frame_stats

            a_verb_stats[ "a_frames_num" ] = len( aa_frames_set)
            a_verb_stats[ "b_verbs_num" ] = len( a_b_verbs_set)
            a_verb_stats[ "b_frames_num" ] = len( a_b_frames_set)
            a_verb_record.stats = a_verb_stats

        stats[ "a_verbs_num" ] = len( a_verbs_set)
        stats[ "a_frames_num" ] = len( a_frames_set)
        stats[ "b_verbs_num" ] = len( b_verbs_set)
        stats[ "b_frames_num" ] = len( b_frames_set)
        self.a_frames_list = list( a_frames_set)
        return stats, list( a_verbs_set)

    def create_verb_table( self):
        with self.tag( "table", klass="table", cellindent="2.0"):
            for verb_ord, a_lemma in enumerate( self.list_of_lemmas):
                a_verb_record = self.dict_of_verbs[ a_lemma ]
                self.process_verb_record( a_verb_record, verb_ord)

    def process_verb_record( self, a_verb_record, verb_ord):
        with self.tag( "tr"):
            with self.tag( "td", klass="verb_help_col"):
                self.text( f"{verb_ord+1}")
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")
            # with self.tag( "td", klass="verb_help_col", colspan=3):
            #     self.text( " ")
            with self.tag( "td", klass="verb_header"):
                with self.tag( "b"):
                    self.text( a_verb_record.lemma)
                self.doc.stag( "br")
                with self.tag( "div", align="right"):
                    self.text( f" {self.a_lang_mark} frames: {a_verb_record.stats[ 'a_frames_num' ]}")
            with self.tag( "td", klass="verb_header", align="left"):
                self.text( f"{self.b_lang_mark} verbs: {a_verb_record.stats[ 'b_verbs_num' ]}")
                self.doc.stag( "br")
                self.text( f"{self.b_lang_mark} frames: {a_verb_record.stats[ 'b_frames_num' ]}")
            with self.tag( "td", klass="verb_aux"):
                self.text( f"Links: {a_verb_record.stats[ 'frame_links_num' ]}")
                self.doc.stag( "br")
                self.text( f"Examples: {a_verb_record.stats[ 'examples_num' ]}")
            with self.tag( "td", klass="verb_aux"):
                self.doc.stag( "input", id=a_verb_record.lemma+"_but", type="button",
                          # onclick=f"button_func( this, '{a_verb_record.lemma}_', \
                          #           {len(a_verb_record.frame_types)})",
                          onclick=f"verb_but_func( this, '{a_verb_record.lemma}')",
                          value="show")

        a_frame_types = [ frame for frame in a_verb_record.frame_types
                         if frame in self.a_frames_list ]
        for frame_ord, a_frame_type in enumerate( a_frame_types): # TODO ZORADIT
            self.process_frame_type( a_frame_type, a_verb_record.lemma, frame_ord)


    def process_frame_type( self, a_frame_type, verb_lemma, frame_ord):
        frame_id = verb_lemma + "_" + str( frame_ord)
        with self.tag( "tr", id=frame_id, klass="hidden", data_group=verb_lemma):
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")
            with self.tag( "td", klass="frame_help_col"):
                self.text( f"{frame_ord+1}")
            with self.tag( "td", klass="frame_help_col"):
                self.text( "")
            with self.tag( "td", klass="frame_header"):
                # TODO JAZYKOVO SPECIVECKE MEDZISPRACOVANIE
                # TODO ZAFARBIT ARGY?
                self.text( a_frame_type.verb_lemma)
                self.doc.stag( "br")
                self.process_a_frame_args( a_frame_type)
                #arguments_list = frame.arguments_to_string().split( ' ')
                # arguments_list = a_frame_type.args_to_one_string().split( ' ')
                # for argument in arguments_list:
                #     self.doc.stag( "br")
                #     self.text( argument)
            with self.tag( "td", klass="frame_header"):
                self.text( f"{self.b_lang_mark} verbs: {a_frame_type.stats[ 'b_verbs_num' ]}")
                self.doc.stag( "br")
                self.text( f"{self.b_lang_mark} frames: {a_frame_type.stats[ 'b_frames_num' ]}")
            with self.tag( "td", klass="frame_aux"):
                self.text( f"Links: {a_frame_type.stats[ 'frame_links_num' ]}")
                self.doc.stag( "br")
                self.text( f"Examples: {a_frame_type.stats[ 'examples_num' ]}")

            with self.tag( "td", klass="frame_aux"):
                self.doc.stag( "input", id=frame_id+"_but", type="button",
                          # onclick=f"button_func( this, '{frame_id}_', \
                          #         {len(a_frame_type.links)})",
                          onclick=f"frame_but_func( this, '{frame_id}')",
                          value="show")
        for link_ord, frame_type_link in enumerate( a_frame_type.links):
            self.process_frame_type_link( frame_type_link, a_frame_type, frame_id, link_ord)

    def process_frame_type_link( self, frame_type_link, a_frame_type, frame_id, link_ord):
        frame_link_id = frame_id + "_" + str( link_ord)
        b_frame_type = frame_type_link.get_other_frame_type( a_frame_type)
        with self.tag( "tr", id=frame_link_id, klass="hidden", data_group=frame_id):
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")
            with self.tag( "td", klass="frame_help_col"):
                self.text( "")
            with self.tag( "td", klass="link_help_col"):
                self.text( f"{link_ord+1}")

            with self.tag( "td", klass="link_header"):
                # TODO JAZYKOVO SPECIVECKE MEDZISPRACOVANIE
                # TODO ZAFARBIT ARGY?
                self.text( a_frame_type.verb_lemma)
                self.doc.stag( "br")
                self.process_a_frame_args_in_link( a_frame_type)
            with self.tag( "td", klass="link_header"):
                # TODO JAZYKOVO SPECIVECKE MEDZISPRACOVANIE
                # TODO ZAFARBIT ARGY?
                self.text( b_frame_type.verb_lemma)
                self.doc.stag( "br")
                self.process_b_frame_args_in_link( b_frame_type, frame_type_link)

            with self.tag( "td", klass="link_aux"):
                self.text( f"Examples: {len(frame_type_link.frame_inst_links)}")
            with self.tag( "td", klass="link_aux"):
                self.doc.stag( "input", id=frame_link_id+"_but", type="button",
                          # onclick=f"button_func( this, '{frame_link_id}_', \
                          #         {len(frame_type_link.frame_inst_links)}) ",
                          onclick=f"link_but_func( this, '{frame_link_id}')",
                          value="show")

        for inst_link_number, frame_inst_link in enumerate( frame_type_link.frame_inst_links):
            self.process_inst_link( frame_inst_link, a_frame_type, frame_link_id, inst_link_number)

    def process_a_frame_args( self, a_frame):
        arg_ord = 1
        for arg in a_frame.args:
            #with self.tag( "div", klass="no_break"):
            arg_str = arg.to_str()
            self.text( arg_str)
            arg.arg_ord = arg_ord
            arg_ord_str = "{" + str( arg.arg_ord) + "}"
            with self.tag( "sub"):
                self.text( arg_ord_str)
            self.text( " ")
            arg_ord += 1

    def process_a_frame_args_in_link( self, a_frame):
        for arg in a_frame.args:
            #with self.tag( "div", klass="no_break"):
            arg_str = arg.to_str()
            self.text( arg_str)
            arg_ord = arg.arg_ord
            arg_ord_str = "{" + str( arg_ord) + "}"
            with self.tag( "sub"):
                self.text( arg_ord_str)
            self.text( " ")

    def process_b_frame_args_in_link( self, b_frame, frame_link):
        for arg_link in frame_link.frame_type_arg_links:
            for b_arg in b_frame.args:
                a_arg = arg_link.get_other_frame_type_arg( b_arg)
                if a_arg:
                    assert hasattr( a_arg, "arg_ord")
                    b_arg.arg_ord = a_arg.arg_ord
                    break
        a_frame = frame_link.get_other_frame_type( b_frame)
        overhang_num = len( a_frame.args) + 1
        for b_arg in b_frame.args:
            #with self.tag( "div", klass="no_break"):
            if not hasattr( b_arg, "arg_ord"):
                b_arg.arg_ord = overhang_num
                overhang_num += 1
            arg_str = b_arg.to_str()
            self.text( arg_str)
            arg_ord = b_arg.arg_ord
            arg_ord_str = "{" + str( arg_ord) + "}"
            with self.tag( "sub"):
                self.text( arg_ord_str)
            self.text( " ")

    def process_inst_link( self, frame_inst_link, a_frame_type, frame_link_id, inst_link_number):
        b_frame_inst = frame_inst_link.get_other_frame_inst_by_type( a_frame_type)
        a_frame_inst = frame_inst_link.get_other_frame_inst( b_frame_inst)

        # for fial in frame_inst_link.frame_inst_arg_links:
        #     self.text( str( fial.link_num))

        inst_link_id = frame_link_id + "_" + str( inst_link_number)

        with self.tag( "tr", id=inst_link_id, klass="hidden", data_group=frame_link_id):
            # INSTANCIE DAVAME NA SAMOSTATNE RIADKY ZATIAL
            #with self.tag( "div", id = examples_id, klass = "hidden"):
            with self.tag( "td", klass="verb_help_col"):
                self.text( " ")
            with self.tag( "td", klass="frame_help_col"):
                self.text( " ")
            with self.tag( "td", klass="link_help_col"):
                self.text( " ")
            with self.tag( "td", klass="examples"):
                self.process_inst( a_frame_inst)
            with self.tag( "td", klass="examples"):
                self.process_inst( b_frame_inst)
            with self.tag( "td", klass="examples_aux", colspan=2):
                pass

    def process_inst( self, frame_inst):
        """ auxiliary method for printing an example sentence
        with the discussed verb and its argments highlighted
        """
        #with self.tag( "p"):

        #with self.tag( "p"):
        # suppose that inst.sentence is not None it was assigned
        for token in frame_inst.sent_tokens:
            if token.is_elided():
                continue
            if token.is_frame_predicate():
                with self.tag( "font", klass="verb"):
                    with self.tag( "b"):
                        self.write_token( token)
            elif token.is_frame_arg():
                with self.tag( "font", klass="arg"):
                    arg_form = "{" + str( self.get_arg_ord_from_token( token)) + "}"
                    self.write_token( token, arg_form)
            else:
                self.write_token( token)
        self.doc.stag( "br")
        elided_tokens_len = len( frame_inst.elided_tokens)
        if elided_tokens_len > 0:
            self.text( " [")
            for i, elided_token in enumerate( frame_inst.elided_tokens):
                # we suppose that elided tokens are frame arguments
                if elided_token.is_frame_predicate():
                    with self.tag("font", klass="verb"):
                        with self.tag("b"):
                            self.write_token( elided_token)
                elif elided_token.is_frame_arg():
                    with self.tag( "font", klass="arg"):
                        arg_form = "{" + str( self.get_arg_ord_from_token( elided_token)) + "}"
                        self.write_elided_token( elided_token, arg_form)
                else:  # elided_token.role == Role.NONE:
                    self.write_token( elided_token)

                if i < elided_tokens_len - 1:
                    self.text( ", ")
                else:
                    self.text( "]")

    @staticmethod
    def get_arg_ord_from_token( token):
        assert token.is_frame_arg()
        arg_inst = token.arg
        arg_type = arg_inst.type
        assert hasattr( arg_type, "arg_ord")
        return arg_type.arg_ord

    def write_token( self, token, arg_form=""):
        self.text( token.form)
        with self.tag( "sub"):
            self.text( arg_form)
        if token.has_space():
            self.text( " ")

    def write_elided_token( self, token, arg_form ):
        if token.form:
            self.text( token.form)
            with self.tag( "sub"):
                self.text( arg_form)
        else:
            self.text( arg_form)


if __name__ == "__main__":
    if 5 <= len( sys.argv) <= 6:
        hc = HTMLer()
        input_file_name = sys.argv[ 1 ]
        a_dict_of_verbs, b_dict_of_verbs = pickle.load( open( input_file_name, "rb" ))
        output_file_name = sys.argv[ 2 ]
        a_lang_mark = sys.argv[ 3 ]
        b_lang_mark = sys.argv[ 4 ]
        if len( sys.argv) >= 6 and sys.argv[ 5 ] == "r":
            hc.create_html( b_dict_of_verbs, output_file_name, b_lang_mark, a_lang_mark)
        else:
            hc.create_html( a_dict_of_verbs, output_file_name, a_lang_mark, b_lang_mark)
    elif len( sys.argv) == 4:
        hc = HTMLer_mono()
        input_file_name = sys.argv[ 1 ]
        dict_of_verbs = pickle.load( open( input_file_name, "rb" ))
        output_file_name = sys.argv[ 2 ]
        lang_mark = sys.argv[ 3 ]
        hc.create_html( dict_of_verbs, output_file_name, lang_mark)
