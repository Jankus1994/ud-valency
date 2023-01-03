import sys, pickle
import xml.etree.ElementTree as et
from vallex.vallex_frame import Vallex_frame
from vallex.vallex_argument import Vallex_argument

class Vallex_loader:
    def __init__( self):
        self.lang_mark = ""

    def process_form( self, vallex_argument, element_form):
        return

    def add_frame_arguments( self, vallex_frame, elements):
        """ processes xml elements, extracts arguments from them
        and adds them to the frame
        """
        new_arguments = set()
        for element in elements:
            vallex_argument = Vallex_argument()
            functor = element.attrib[ "functor" ]
            vallex_argument.set_functor( functor)

            form = element.find( "form")  # might be None
            self.process_form( vallex_argument, form)

            element_type = element.attrib[ "type" ]
            vallex_argument.set_arg_type( element_type)

            vallex_frame.add_argument( vallex_argument)

    def get_dictionary( self, root): #
        """ processes vallex xml file, extracts verb frames and saves it into pickle """
        vallex_dict = {}
        output_str = ""
        word_elements = root.findall( ".//word")
        lemmas = []
        lemma_number = 0
        for word_element in word_elements:
            lemma = word_element.attrib[ "lemma" ]
            lemmas.append( lemma)
            lemma_number += 1
            if lemma not in vallex_dict:
                vallex_dict[ lemma ] = []
            frames = word_element.findall( ".//frame")
            for frame in frames:
                frame_id = frame.attrib[ "id" ]
                vallex_frame = Vallex_frame( self.lang_mark, frame_id)
                #output_str += lemma + '\n'
                vallex_frame.set_lemmas( [lemma])
    
                elements = frame.findall( ".//element")
                self.add_frame_arguments( vallex_frame, elements)
    
                output_str += '\n'
                examples = frame.findall( ".//example")
                for example in examples:
                    output_str += '\t' + example.text + '\n'
                    vallex_frame.add_example( example)
    
                output_str += "=======================" + '\n'
                #vallex_frames.append( vallex_frame)
                vallex_dict[ lemma ].append( vallex_frame)

        print( len( lemmas))
        print( lemma_number)
        print( len( vallex_dict))
        return vallex_dict


    def load( self, input_name, output_name):
        tree = et.ElementTree( file=input_name)
        root = tree.getroot()

        vallex_dict = self.get_dictionary( root)
    
        pickle.dump( vallex_dict, open( output_name, 'wb'))
    
if __name__ == "__main__":
    if len( sys.argv) == 3:
        vallex_loader = Vallex_loader()
        input_name = sys.argv[ 1 ] # "../data/vallex_3.0.xml"
        output_name = sys.argv[ 2 ] # "../data/vallex_frames.pic"
        vallex_loader.load( input_name, output_name)    
