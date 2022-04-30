import sys, pickle
import logging, daiquiri
from yattag import *  # yattag trick: "klass" will be replaced with "class"
import re
#from role import Role
from udapi.block.valency import *
doc, tag, text = Doc().tagtext()
daiquiri.setup( level = logging.DEBUG)
logger = daiquiri.getLogger()

class HTML_creator:
    def __init__( self):
        self.column_names = [ "SHOW", "", "ARGUMENTS", "TRANS LEMMA", \
                         "", "TRANS ARGS", "STATS" ]
        self.dict_of_verbs = None
        self.list_of_lemmas = None
    def create_html( self, dict_of_verbs, output_file_name):
        """ main method for creating an HTML table
        with verb frames using yattag liberary
        """
        logger.info( "Creating HTML...")
        self.dict_of_verbs = dict_of_verbs
        self.list_of_lemmas = sorted( self.dict_of_verbs.keys())
        doc.asis( "<!DOCTYPE html>")

        with tag( "html"):
            self.html_head()
            self.html_body()

        val = doc.getvalue()
        #ind = indent( val)
        with open( output_file_name, 'w') as output_file:
            output_file.write( val)#ind)
        logger.info( "HTML created.")

    def html_head( self):
        with tag( "head"):
            with tag( "title"):
                text( "Table of verb frames")
            with tag( "meta", charset = "UTF-8"):
                pass
            with tag( "link", rel = "stylesheet", href = "output.css"):
                pass

            with tag( "style"):
                text( ".hidden{ display:none; }")
                text( ".shown{ display:block; }")
            with tag( "script", type = "text/javascript", src = "info_showing.js"):
                pass

    def html_body( self):
        with tag( "body"):
            with tag( "p"):
                text( "Total number of verbs: ")
                text( len( self.list_of_lemmas))
            with tag( "p"):
                verb_records = [ self.dict_of_verbs[ lemma ] \
                                for lemma in self.list_of_lemmas ]
                verb_frame_types = [ frame_type for verb_record in verb_records \
                                    for frame_type in verb_record.frame_types ]
                text( "Total number of verb frames: ")
                text( len( verb_frame_types))

                self.create_verb_table()

    def create_verb_table( self): 
        with tag( "table", klass = "table", cellindent = "2.0"):
            with tag( "tr"):
                for column_name in self.column_names:
                    with tag( "th"):
                        text( column_name)
            for a_lemma in self.list_of_lemmas:
                a_verb_record = self.dict_of_verbs[ a_lemma ]
                self.process_verb_record( a_verb_record, a_lemma)

    def process_verb_record( self, a_verb_record, a_lemma):
        with tag( "tr"):
            with tag( "td", klass = "verb_header", colspan = str( len( self.column_names))):
                with tag( "b"):
                    text( a_lemma)
                text( " (" + str( len( a_verb_record.frame_types)) + ")")
        a_frame_type_number = 0

        for a_frame_type in a_verb_record.frame_types:
            self.process_frame_type( a_frame_type, a_frame_type_number, a_lemma)
            a_frame_type_number += 1
        
        with tag( "tr"): # empty row between two verb records
            with tag( "td", colspan = str( len( self.column_names))):
                doc.stag( "br")

    def process_frame_type( self, a_frame_type, a_frame_type_number, a_lemma):
        examples_id = a_lemma + str( a_frame_type_number)
        number_of_links = str( len( a_frame_type.links))
        with tag( "tr"):
            with tag( "td", klass = "middle_col"):
                # TU ASI BUDE TREBA DAT RAWSPAN
                doc.stag( "input", type = "button",
                            onclick = "show( this, '" + examples_id + "', " + \
                                    number_of_links + ") ",
                            value = "show")                            
            with tag( "td", klass = "small_col"):
                pass
                #text( a_frame_type.verb_form + a_frame_type.voice)
            with tag( "td", klass = "large_col"):
                #arguments_list = frame.arguments_to_string().split( ' ') 
                arguments_list = a_frame_type.args_to_one_string().split( ' ')
                for argument in arguments_list:
                    text( argument)
                    doc.stag( "br")
            with tag( "td", klass = "large_col", colspan = str( 3)):
                pass
            with tag( "td", klass = "small_col"):
                text( "links: " + str( len( a_frame_type.links)))
                doc.stag( "br")
                paired_insts = [ frame_inst for frame_inst in a_frame_type.insts \
                                            if frame_inst.link is not None ]
                text( "ex: " +  str( len( paired_insts)) + "/" + \
                        str( len( a_frame_type.insts)))
        
        frame_type_link_number = 0
        for frame_type_link in a_frame_type.links:
            link_examples_id = examples_id + str( frame_type_link_number)
            self.process_frame_type_link( frame_type_link, link_examples_id)
            frame_type_link_number += 1


    def process_frame_type_link( self, frame_type_link, link_examples_id):
        with tag( "tr"):
            with tag( "td", klass = "small_col"):
                pass
            with tag( "td", colspan = str( 6)):
                with tag( "div", id = link_examples_id, klass = "hidden"):
                    with tag( "table", klass = "table", cellindent = "2.0"):
                        for frame_type_arg_link in frame_type_link.frame_type_arg_links:
                            link_num = str( frame_type_arg_link.get_link_num())
                            a_frame_type_arg = frame_type_arg_link.a_frame_type_arg
                            b_frame_type_arg = frame_type_arg_link.b_frame_type_arg
                            with tag( "tr"):
                                with tag( "td", klass = "small_col"):
                                    pass
                                with tag( "td", klass = "large_col"):
                                    a_arg_string = a_frame_type_arg.to_string()
                                    #a_arg_num = str( a_frame_type_arg.get_arg_num())
                                    text( a_arg_string + ".{"+ link_num + "}")
                                with tag( "td", klass = "middle_col"):
                                    pass
                                with tag( "td", klass = "large_col"):
                                    b_arg_string = b_frame_type_arg.to_string()
                                    #b_arg_num = str( b_frame_type_arg.get_arg_num())
                                    text( b_arg_string + ".{" + link_num + "}")

                        a_frame_type = frame_type_link.a_frame_type
                        b_frame_type = frame_type_link.b_frame_type
                        with tag( "tr"):
                            with tag( "td", klass = "small_col"):
                                pass
                            with tag( "td", klass = "large_col"):
                                for a_frame_type_arg in a_frame_type.args:
                                    a_arg_string = a_frame_type_arg.to_string()
                                    #a_arg_num = str( a_frame_type_arg.get_arg_num())
                                    text( a_arg_string)# + ".{" + a_arg_num + "}")
                                    doc.stag( "br")
                            with tag( "td", klass = "middle_col"):
                                b_lemma = b_frame_type.verb_lemma
                                text( b_lemma)
                            #with tag( "td", klass = "small_col"):
                            #    pass
                            with tag( "td", klass = "large_col"):
                                for b_frame_type_arg in b_frame_type.args:
                                    b_arg_string = b_frame_type_arg.to_string()
                                    #b_arg_num = b_frame_type_arg.get_arg_num()
                                    text( b_arg_string)# + ".{" + str( b_arg_num) + "}")
                                    doc.stag( "br")
                            with tag( "td", klass = "small_col"):
                                text( "ex: " + str( len( frame_type_link.frame_inst_links)))
                        for frame_inst_link in frame_type_link.frame_inst_links:
                            self.process_inst_link( frame_inst_link)

    def process_inst_link( self, frame_inst_link):
        a_frame_inst = frame_inst_link.a_frame_inst
        b_frame_inst = frame_inst_link.b_frame_inst

        for fial in frame_inst_link.frame_inst_arg_links:
            text( str( fial.link_num))

        with tag( "tr"):
            # INSTANCIE DAVAME NA SAMOSTATNE RIADKY ZATIAL
            #with tag( "div", id = examples_id, klass = "hidden"):
            with tag( "td", klass = "examples", colspan = str( 2)):
                self.process_inst( a_frame_inst)
            with tag( "td", klass = "examples", colspan = str( 2)): #colspan = str( 3)):
                self.process_inst( b_frame_inst)
            with tag( "td", klass = "small_col"):
                pass

    def process_inst( self, frame_inst):
        """ auxiliary method for printing an example sentence
        with the discussed verb and its argments highlighted
        """
        #with tag( "p"):
            
        #return
        with tag( "p"):
            # suppose that inst.sentence is not None it was assigned 
            for token in frame_inst.sent_tokens:
                if token.is_elided():
                    continue
                token_form = token.get_form()

                if token.is_frame_predicate():
                    with tag( "font", klass = "verb"):
                        with tag( "b"):
                            self.write_token( token, token_form)
                elif token.is_frame_arg():
                    with tag( "font", klass = "arg"):
                        token_form += ".{" + str( token.get_arg_num()) + "}"
                        self.write_token( token, token_form)
                else:
                    self.write_token( token, token_form)
            
            elided_tokens = [ token for token in frame_inst.sent_tokens \
                              if token.is_elided() ]
            elided_tokens_len = len( elided_tokens)
            if elided_tokens_len > 0:
                text( " [")
                for i, elided_token in enumerate( elided_tokens):
                    # we suppose that elided tokens are frame arguments
                    with tag( "font", klass = "arg"):
                        if elided_token.is_frame_predicate():
                            with tag("font", klass = "verb"):
                                with tag("b"):
                                    self.write_token( token, elided_token.form)
                        elif elided_token.is_frame_arg():
                            with tag( "font", klass = "arg"):
                                token_form += ".{" + str( token.get_arg_num()) + "}"
                                self.write_token( token, elided_token.form)
                        else:  # elided_token.role == Role.NONE:
                            self.write_token( token, elided_token.form)
                        
                    if i < elided_tokens_len - 1:
                        text( ", ")
                    else:
                        text( "]")

    def write_token( self, token, token_form):
        if token.has_space():
            token_form += " "
        text( token_form)

                    
if ( len( sys.argv) == 3 ):
    hc = HTML_creator()
    input_file_name = sys.argv[ 1 ]
    cs_dict_of_verbs, en_dict_of_verbs = pickle.load( open( input_file_name, "rb" ))
    output_file_name = sys.argv[ 2 ]
    hc.create_html( cs_dict_of_verbs, output_file_name)
