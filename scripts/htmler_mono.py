import sys, pickle
from yattag import *  # yattag trick: "klass" will be replaced with "class"
from collections import Counter


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

class HTMLer_mono:
    def __init__( self):
        # self.column_names = [ "SHOW", "", "ARGUMENTS", "TRANS LEMMA", \
        #                  "", "TRANS ARGS", "STATS" ]
        self.colnum = 3
        self.dict_of_verbs = None
        self.list_of_lemmas = None
        self.a_frames_list = None
        self.lang_mark = ""
        
        self.doc, self.tag, self.text = Doc().tagtext()

    def create_html( self, dict_of_verbs, output_file_name, lang_mark):
        """ main method for creating an HTML table
        with verb frames using yattag liberary
        """
        print( "Creating HTML...", file=sys.stderr)
        self.lang_mark = lang_mark
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
                self.text( f"{self.lang_mark} valency dictionary")
            with self.tag( "table", klass="table", cellindent="2.0"):
                stats = self.compute_overall_stats()
                self.list_of_lemmas = sorted( [ lemma for lemma in self.dict_of_verbs.keys()],
                                             key=CUSTOM_SORT_KEYS[self.lang_mark])
                self.text( f"Verbs: {stats['verbs_num']}")
                self.doc.stag( "br")
                self.text( f"Frames: {stats['frames_num']}")
                self.doc.stag( "br")
                self.text( f"Examples: {stats['examples_num']}")
            self.doc.stag( "br")
            self.create_verb_table()

    def compute_overall_stats( self):
        stats = Counter()
        stats[ "verbs_num" ] = len( self.dict_of_verbs)
        for verb_record in self.dict_of_verbs.values():
            verb_stats = Counter()
            verb_stats["frames_num"] = len( verb_record.frame_types)
            stats[ "frames_num" ] += len( verb_record.frame_types)
            for frame_type in verb_record.frame_types:
                frame_stats = { "examples_num": len( frame_type.insts) }
                verb_stats[ "examples_num" ] += len( frame_type.insts)
                stats[ "examples_num" ] += len( frame_type.insts)
                frame_type.stats = frame_stats
            verb_record.stats = verb_stats
        return stats

    def create_verb_table( self):
        with self.tag( "table", klass="table", cellindent="2.0"):
            for verb_ord, a_lemma in enumerate( self.list_of_lemmas):
                a_verb_record = self.dict_of_verbs[ a_lemma ]
                self.process_verb_record( a_verb_record, verb_ord)

    def process_verb_record( self, verb_record, verb_ord):
        with self.tag( "tr"):
            with self.tag( "td", klass="verb_help_col"):
                self.text( f"{verb_ord+1}")
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")

            with self.tag( "td", klass="verb_header"):
                with self.tag( "b"):
                    self.text( verb_record.lemma)
            with self.tag( "td", klass="verb_aux"):
                self.text( f"Frames: {verb_record.stats['frames_num']}")
                self.doc.stag( "br")
                self.text( f"Examples: {verb_record.stats['examples_num']}")
            with self.tag( "td", klass="verb_aux"):
                self.doc.stag( "input", id=verb_record.lemma + "_but", type="button",
                          # onclick=f"button_func( this, '{a_verb_record.lemma}_', \
                          #           {len(a_verb_record.frame_types)})",
                          onclick=f"mono_verb_but_func( this, '{verb_record.lemma}')",
                          value="show")

        for frame_ord, frame_type in enumerate( verb_record.frame_types): # TODO ZORADIT
            self.process_frame_type( frame_type, verb_record.lemma, frame_ord)

    def process_frame_type(self, frame_type, verb_lemma, frame_ord):
        frame_id = verb_lemma + "_" + str( frame_ord)
        with self.tag( "tr", id=frame_id, klass="hidden", data_group=verb_lemma):
            with self.tag( "td", klass="verb_help_col"):
                self.text( "")
            with self.tag( "td", klass="frame_help_col"):
                self.text( f"{frame_ord+1}")
            with self.tag( "td", klass="frame_header"):
                # TODO JAZYKOVO SPECIVECKE MEDZISPRACOVANIE
                # TODO ZAFARBIT ARGY?
                self.process_frame_args( frame_type)
            with self.tag( "td", klass="frame_aux"):
                self.text( f"Examples: {frame_type.stats['examples_num']}")
            with self.tag( "td", klass="frame_aux"):
                self.doc.stag( "input", id=frame_id+"_but", type="button",
                          onclick=f"mono_frame_but_func( this, '{frame_id}')",
                          value="show")

        for inst_ord, frame_inst in enumerate( frame_type.insts):
            self.process_inst( frame_inst, frame_id, inst_ord)

    def process_frame_args( self, frame):
        arg_ord = 1
        for arg in frame.args:
            #with self.tag( "div", klass="no_break"):
            arg_str = arg.to_str()
            self.text( arg_str)
            arg.arg_ord = arg_ord
            arg_ord_str = "{" + str( arg.arg_ord) + "}"
            with self.tag( "sub"):
                self.text( arg_ord_str)
            self.text( " ")
            arg_ord += 1

    def process_inst( self, frame_inst, frame_id, inst_ord):
        """ auxiliary method for printing an example sentence
        with the discussed verb and its argments highlighted
        """
        inst_id = frame_id + "_" + str( inst_ord)
        with self.tag( "tr", id=inst_id, klass="hidden", data_group=frame_id):
            # INSTANCIE DAVAME NA SAMOSTATNE RIADKY ZATIAL
            #with self.tag( "div", id = examples_id, klass = "hidden"):
            with self.tag( "td", klass="verb_help_col"):
                self.text( " ")
            with self.tag( "td", klass="frame_help_col"):
                self.text( " ")

            with self.tag( "td", klass="examples", colspan=3):
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
                            with self.tag( "font", klass="verb"):
                                with self.tag( "b"):
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

            # with self.tag( "td", klass="examples_aux", colspan=2):
            #     pass

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

