import sys, pickle
import logging, daiquiri
from yattag import *  # yattag trick: "klass" will be replaced with "class"
import re
doc, tag, text = Doc().tagtext()
daiquiri.setup( level = logging.DEBUG)
logger = daiquiri.getLogger()

class HTML_creator:
    def __init__( self):
        self.column_names = [ "SHOW", "", "ARGUMENTS", "TRANS LEMMA", \
                         "", "TRANS ARGS", "STATS" ]
        self.dict_of_verbs = None
        self.list_of_lemmas = None
    def create_html( self, dict_of_verbs):
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
        print( val)#ind)
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
                verb_records = [ self.dict_of_verbs[ lemma ] for lemma in self.list_of_lemmas ]
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
        number_of_links = str( len( a_frame_type.frame_links))
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
                text( "links: " + str( len( a_frame_type.frame_links)))
                doc.stag( "br")
                paired_instances = [ instance for instance in a_frame_type.instances \
                                            if instance.frame_link is not None ]
                text( "ex: " +  str( len( paired_instances)) + "/" + \
                        str( len( a_frame_type.instances)))
        
        frame_link_number = 0
        for frame_link in a_frame_type.frame_links:
            link_examples_id = examples_id + str( frame_link_number)
            self.process_frame_link( frame_link, link_examples_id)
            frame_link_number += 1


    def process_frame_link( self, frame_link, link_examples_id):
        with tag( "tr"):
            with tag( "td", klass = "small_col"):
                pass
            with tag( "td", colspan = str( 6)):
                with tag( "div", id = link_examples_id, klass = "hidden"):
                    with tag( "table", klass = "table", cellindent = "2.0"):
                        b_frame_type = frame_link.b_frame_type
                        with tag( "tr"):
                            with tag( "td", klass = "small_col"):
                                pass
                            with tag( "td", klass = "large_col"):
                                #with tag( "p"):
                                #    text( str( frame_link))
                                pass
                            with tag( "td", klass = "middle_col"):
                                b_lemma = b_frame_type.verb_lemma
                                text( b_lemma)
                            #with tag( "td", klass = "small_col"):
                            #    pass
                            with tag( "td", klass = "large_col"):
                                arguments_list = b_frame_type.args_to_one_string().split( ' ')
                                for argument in arguments_list:
                                    text( argument)
                                    doc.stag( "br")
                            with tag( "td", klass = "small_col"):
                                text( "ex: " + str( len( frame_link.frame_instance_pairs)))
                        for frame_instance_pair in frame_link.frame_instance_pairs:
                            self.process_instance_pair( frame_instance_pair)

    def process_instance_pair( self, frame_instance_pair):
        a_frame_instance = frame_instance_pair[ 0 ]
        b_frame_instance = frame_instance_pair[ 1 ]
        with tag( "tr"):
            # INSTANCIE DAVAME NA SAMOSTATNE RIADKY ZATIAL
            #with tag( "div", id = examples_id, klass = "hidden"):
            with tag( "td", klass = "examples", colspan = str( 2)):
                self.process_instance( a_frame_instance)
            with tag( "td", klass = "examples", colspan = str( 2)): #colspan = str( 3)):
                self.process_instance( b_frame_instance)
            with tag( "td", klass = "small_col"):
                pass

    def process_instance( self, instance):
        """ auxiliary method for printing an example sentence
        with the discussed verb and its argments highlighted
        """
        #with tag( "p"):
            
        #return
        with tag( "p"):
            for token in instance.sentence.tokens:
                token_form = token[ "form" ]
                if ( token[ "space" ] ):
                    token_form += " "

                if ( token[ "highlight" ] == 2 ):
                    with tag( "font", klass = "verb"):
                        with tag( "b"):
                            text( token_form)
                elif ( token[ "highlight" ] == 1 ):
                    with tag( "font", klass = "arg"):
                        text( token_form)
                else:
                    text( token_form)

            elided_tokens_len = len( instance.sentence.elided_tokens)
            if elided_tokens_len > 0:
                text( " [")
                for i, elided_token in enumerate( instance.sentence.elided_tokens):
                    with tag( "font", klass = "arg"):  # we suppose that elided tokens are frame arguments
                        elided_token_form = elided_token[ "form" ]
                        
                        if token[ "highlight" ] == 2:
                            with tag("font", klass = "verb"):
                                with tag("b"):
                                    text( elided_token_form)
                        elif token[ "highlight" ] == 1:
                            with tag( "font", klass = "arg"):
                                text( elided_token_form)
                        else:
                            text( elided_token_form)
                        
                    if i < elided_tokens_len - 1:
                        text( ", ")
                    else:
                        text( "]")

                    
if ( len( sys.argv) == 2 ):
    hc = HTML_creator()
    cs_dict_of_verbs, en_dict_of_verbs = pickle.load( open( sys.argv[ 1 ], "rb" ))
    hc.create_html( cs_dict_of_verbs)
