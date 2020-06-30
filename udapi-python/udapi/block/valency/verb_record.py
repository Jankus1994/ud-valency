from udapi.block.valency.frame import Frame_type

class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        self.frame_type_class = Frame_type

        self.lemma = lemma
        self.frame_types = []

    def process_frame( self, verb_node):  # -> Frame
        """ creates a verb frame for a given verb node """
        new_frame_type = self.frame_type_class( verb_node)
        for frame_type in self.frame_types:
            success = frame_type.try_merge_with( new_frame_type)
            if success:
                break
        else:
            self.frame_types.append( new_frame_type)
        frame_instance = new_frame_type.get_instance()
        return frame_instance

