from frame_extractor import Frame_extractor
from dict_printer import Dict_printer

class Base_frame_extractor( Frame_extractor):
    def __init__( self, **kwargs):
        super().__init__( **kwargs)
        self.appropriate_udeprels = \
                [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]

    def adding_missng_subjects( self, frame_type, frame_inst, _):
        return frame_type, frame_inst

    def _could_be_coord_arg( self, _, __):
        return False

    def _consider_aux_form( self, frame_type_arg, arg_node):
        return frame_type_arg

    def after_process_document( self, doc):  # void
        self._check_coherence()
        Dict_printer.print_dict( self.output_form, self.dict_of_verbs, self.output_name)