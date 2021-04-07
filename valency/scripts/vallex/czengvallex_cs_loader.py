import sys
from vallex_argument import Vallex_argument
from vallex_loader import Vallex_loader

class Czengvallex_cs_loader( Vallex_loader):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.lang_mark = "cs"

    def process_form( self, vallex_argument, element_form):
        if element_form is None:
            vallex_argument.set_form( "")
            return
        form_nodes = element_form.findall( "node")
        for form_node in form_nodes:
            if form_node is not None:
                if "case" in form_node.attrib:
                    case = form_node.attrib[ "case" ]
                    vallex_argument.set_form( case)
                    break


if __name__ == "__main__":
    if len( sys.argv) == 3:
        input_name = sys.argv[ 1 ] # "../data/vallex_3.0.xml"
        output_name = sys.argv[ 2 ] # "../data/vallex_frames.pic"
        vallex_loader = Czengvallex_cs_loader()
        vallex_loader.load( input_name, output_name)

