import sys
import xml.etree.ElementTree as et
from vallex.vallex_frame import Vallex_frame
from vallex.vallex_loader import Vallex_loader

class Cs_vallex_loader( Vallex_loader):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.lang_mark = "cs"

    def process_form( self, vallex_argument, slot_form):
        subord_conj_lemma = ""
        prepos_lemma = ""
        case = ""
        if slot_form is not None:
            if "subord_conj_lemma" in slot_form.attrib:
                subord_conj_lemma = slot_form.attrib[ "subord_conj_lemma" ]
            if "prepos_lemma" in slot_form.attrib:
                prepos_lemma = slot_form.attrib[ "prepos_lemma" ]
            if "case" in slot_form.attrib:
                case = slot_form.attrib[ "case" ]
        form = subord_conj_lemma + '-' + prepos_lemma + '-' + case
        vallex_argument.set_form( form)
    
    
    def get_dictionary( self, root): #
        """ processes vallex xml file, extracts verb frames and saves it into pickle """
        tree = et.ElementTree( file=input_name)
        root = tree.getroot()
        vallex_dict = {}
        output_str = ""
        lexemes = root.findall( ".//lexeme")
        lemma_number = 0
        for lexeme in lexemes:
            mlemmas = lexeme.findall( ".//mlemma")
            lemmas = list( set( [ mlemma.text for mlemma in mlemmas ]))
            lemma_number += len( lemmas)
            for lemma in lemmas:
                if lemma not in vallex_dict:
                    vallex_dict[ lemma ] = []
    
            commonrefl = lexeme.find( ".//commonrefl")
            refl = None
            if commonrefl is not None:
                refl = commonrefl.text
    
            lexical_units = lexeme.findall( ".//blu")
            for lexical_unit in lexical_units:
                frame_id = lexical_unit.attrib[ "id" ]
                vallex_frame = Vallex_frame( self.lang_mark, frame_id)
                #output_str += lemma + '\n'
                vallex_frame.set_lemmas( lemmas)
                vallex_frame.set_refl( refl)
    
                slots = lexical_unit.findall( ".//slot")
                self.add_frame_arguments( vallex_frame, slots)
    
                output_str += '\n'
                lu_gloss = lexical_unit.find( "gloss")
                lu_example = lexical_unit.find( "example")
                glosses = list( lu_gloss.itertext())
                examples = list( lu_example.itertext())
                #coindexeds = lu_example.findall( "coindexed")
                #coindexed_text = [ coindexed.text for coindexed in coindexeds ]
                #examples = example_text.split( "; ")
                #coindexed_examples = "; ".join( coindexed_text).split( "; ")
                for example in glosses + examples:# + coindexed_examples:
                    output_str += '\t' + example + '\n'
                    vallex_frame.add_example( example.strip())
    
                output_str += "======================="  + '\n'
                #vallex_frames.append( vallex_frame)
                for lemma in vallex_frame.lemmas:
                    vallex_dict[ lemma ].append( vallex_frame)
        
        print( len( lexemes))
        print( lemma_number)
        print( len( vallex_dict))
        return vallex_dict
    
if __name__ == "__main__":
    if len( sys.argv) == 3:
        input_name = sys.argv[ 1 ] # "../data/vallex_3.0.xml"
        output_name = sys.argv[ 2 ] # "../data/vallex_frames.pic"
        vallex_loader = Cs_vallex_loader()
        vallex_loader.load( input_name, output_name)

