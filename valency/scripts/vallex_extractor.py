import pickle

import sys
import xml.etree.ElementTree as et

class Vallex_argument:
    def __init__( self):
        self.functor = None
        self.subord_conj_lemma = None
        self.prepos_lemma = None
        self.case = None
        self.arg_type = None
    def set_functor( self, functor):
        self.functor = functor
    def set_form( self, slot_form):
        try:
            self.subord_conj_lemma = slot_form.attrib[ "subord_conj_lemma" ]
        except KeyError:
            pass
        try:
            self.prepos_lemma = slot_form.attrib[ "prepos_lemma" ]
        except KeyError:
            pass
        try:
            self.case = slot_form.attrib[ "case" ]
        except KeyError:
            pass
    def set_arg_type( self, arg_type):
        self.arg_type = arg_type
    def to_string( self):
        string = self.functor
        if self.subord_conj_lemma is not None:
            string += '-' + self.subord_conj_lemma
        if self.prepos_lemma is not None:
            string += '-' + self.prepos_lemma
        if self.case is not None:
            string += '-' + self.case
        if self.arg_type in [ "typ", "opt" ]:
            string = '(' + string + ')'
        return string

class Vallex_record:
    def __init__( self):
        self.lemmas = None
        self.refl = None
        self.arguments = []
        self.examples = []
    def set_lemmas( self, lemmas):
        self.lemmas = lemmas
    def set_refl( self, refl):
        self.refl = refl
    def add_argument( self, argument):
        self.arguments.append( argument)
    def add_example( self, example):
        self.examples.append( example)
    def args_string( self):
        args_str_list = [ arg.to_string() for arg in self.arguments ]
        args_str = ' '.join( args_str_list)
        return args_str

def extract( input_name, output_name): #
    """ processes vallex xml file, extracts verb frames and saves it into pickle """
    tree = et.ElementTree( file=input_name)
    root = tree.getroot()
    #vallex_records = []
    vallex_dict = {}
    output_str = ""
    lexemes = root.findall( ".//lexeme")
    for lexeme in lexemes:
        mlemmas = lexeme.findall( ".//mlemma")
        lemmas = list( set( [ mlemma.text for mlemma in mlemmas ]))
        for lemma in lemmas:
            if lemma not in vallex_dict:
                vallex_dict[ lemma ] = []

        commonrefl = lexeme.find( ".//commonrefl")
        refl = None
        if commonrefl is not None:
            refl = commonrefl.text

        lexical_units = lexeme.findall( ".//blu")
        for lexical_unit in lexical_units:
            vallex_record = Vallex_record()
            #output_str += lemma + '\n'
            vallex_record.set_lemmas( lemmas)
            vallex_record.set_refl( refl)

            slots = lexical_unit.findall( ".//slot")
            for slot in slots:
                vallex_argument = Vallex_argument()
                slot_functor = slot.attrib[ "functor" ]
                vallex_argument.set_functor( slot_functor)
                
                slot_form = slot.find( "form")
                if slot_form is not None:
                    vallex_argument.set_form( slot_form)
                
                slot_type = slot.attrib[ "type" ] 
                vallex_argument.set_arg_type( slot_type)
                
                vallex_record.add_argument( vallex_argument)

            output_str += '\n'
            lu_example = lexical_unit.find( "example")
            example_text = lu_example.text.strip()
            coindexeds = lu_example.findall( "coindexed")
            coindexed_text = [ coindexed.text for coindexed in coindexeds ]
            examples = example_text.split( "; ")
            coindexed_examples = "; ".join( coindexed_text).split( "; ")
            for example in examples + coindexed_examples:
                output_str += '\t' + example + '\n'
                vallex_record.add_example( example)

            output_str += "======================="  + '\n'
            #vallex_records.append( vallex_record)
            for lemma in vallex_record.lemmas:
                vallex_dict[ lemma ].append( vallex_record)


    pickle.dump( vallex_dict, open( output_name, 'wb'))

if __name__ == "__main__":
    if len( sys.argv) == 3:
        input_name = sys.argv[ 1 ] # "../data/vallex_3.0.xml"
        output_name = sys.argv[ 2 ] # "../data/vallex_records.pic"
    extract( input_name, output_name)
