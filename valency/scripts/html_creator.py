import sys, pickle
import logging, daiquiri
from yattag import *
import re
doc, tag, text = Doc().tagtext()
daiquiri.setup( level = logging.DEBUG)
logger = daiquiri.getLogger()

class HTML_creator:
    def create_table( self, dict_of_verbs):
        """ main method for creating an HTML table
        with verb frames using yattag liberary
        """
        logger.info( "Creating HTML...")
        list_of_lemmas = sorted( dict_of_verbs.keys())
        column_names = [ "SHOW", "FORM", "VOICE", "ARGUMENTS", "FREQUENCY" ]
        
        doc.asis( "<!DOCTYPE html>")
        with tag( "html"):
            with tag( "head"):
                with tag( "title"):
                    text( "Table of verb frames")
                with tag( "meta", charset = "UTF-8"):
                    pass
                with tag( "link", rel = "stylesheet", href = "output.css"):
                    pass
                
                # functionality of buttons showing example sentences
                with tag( "style"):
                    text( ".hidden{ display:none; }")
                    text( ".shown{ display:block; }")
                with tag( "script", type = "text/javascript", src = "info_showing.js"):
                    pass
                #
                
            with tag( "body"):
                with tag( "p"):
                    text( "Total number of verbs: ")
                    text( len( list_of_lemmas))
                with tag( "p"):
                    verb_records = [ dict_of_verbs[ lemma ] for lemma in list_of_lemmas ]                    
                    verb_frames = [ frame for verb_record in verb_records for frame in verb_record.frames ]
                    text( "Total number of verb frames: ")
                    text( len( verb_frames))

                with tag( "table", klass = "table", cellindent = "2.0"):
                    with tag( "tr"):
                        for column_name in column_names:
                            with tag( "th"):
                                text( column_name)
                    for lemma in list_of_lemmas:
                        verb_record = dict_of_verbs[ lemma ]
                        with tag( "tr"):
                            with tag( "td", klass = "verb_header",
                                     colspan = str( len( column_names))):
                                with tag( "b"):
                                    text( lemma)
                                text( " (" + str( len( verb_record.frames)) + ")")
                        frame_number = 0
                        for frame in verb_record.frames:
                            examples_id = lemma + str( frame_number)
                            with tag( "tr"):
                                with tag( "td", klass = "middle_col"):
                                    doc.stag( "input", type = "button",
                                             onclick = "show( this, '" + examples_id + "') ",
                                             value = "show")                            
                                with tag( "td", klass = "middle_col"):
                                    text( frame.verb_form)
                                with tag( "td", klass = "middle_col"):
                                    text( frame.voice)
                                with tag( "td", klass = "large_col"):
                                    #arguments_list = frame.arguments_to_string().split( ' ') 
                                    arguments_list = frame.args_to_one_string().split( ' ')
                                    for argument in arguments_list:
                                        text( argument)
                                        doc.stag( "br")
                                with tag( "td", klass = "small_col"):
                                    text( str( frame.frequency))
                            with tag( "tr"):
                                with tag( "td", klass = "middle_col"):
                                    pass
                                with tag( "td", klass = "examples", 
                                         colspan = str( len( column_names) - 1)):                                    
                                    with tag( "div", id = examples_id, klass = "hidden"):
                                        # yattag trick: klass will be replaced with class
                                        for sentence in frame.example_sentences:
                                            self.build_example_sentence( sentence)
                            frame_number += 1
                        
                        with tag( "tr"): # empty row between two verb records
                            with tag( "td", colspan = str( len( column_names))):
                                doc.stag( "br")        

        val = doc.getvalue()
        #ind = indent( val)                    
        print( val)#ind)
        logger.info( "HTML created.")
    
    def build_example_sentence( self, sentence):
        """ auxiliary method for printing an example sentence
        with the discussed verb and its argments highlighted
        """
        with tag( "p"):
            for token in sentence.tokens:
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

                    
if ( len( sys.argv) == 2 ):
    hc = HTML_creator()
    dict_of_verbs = pickle.load( open( sys.argv[ 1 ], "rb" ))
    hc.create_table( dict_of_verbs)
