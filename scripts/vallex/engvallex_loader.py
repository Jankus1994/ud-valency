import sys
from vallex.vallex_loader import Vallex_loader

class Engvallex_loader( Vallex_loader):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.lang_mark = "en"


    def process_form( self, vallex_argument, element_form):
        form_value = ""
        if element_form is not None:
            form_value = element_form.attrib[ "value" ]
        vallex_argument.set_form( form_value)


if __name__ == "__main__":
    if len( sys.argv) == 3:
        input_name = sys.argv[ 1 ] # "../data/vallex_3.0.xml"
        output_name = sys.argv[ 2 ] # "../data/vallex_frames.pic"
        vallex_loader = Engvallex_loader()
        vallex_loader.load( input_name, output_name)

