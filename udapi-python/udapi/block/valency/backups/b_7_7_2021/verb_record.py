from udapi.block.valency.frame import Frame_type

class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        """ called from Frame_extractor.process_node """
        self.lemma = lemma
        self.frame_types = []

    def consider_new_frame_type( self, new_frame_type, new_frame_inst):  # void
        """ called from Frame_extractor.process_frame
        gets a Frame_type and its (first) Frame_inst
        controls if this Frame_type is already present in the list and if yes,
        the new instance is only added to it
        """
        # comparing with already existing frames
        for frame_type in self.frame_types:
            if frame_type.is_identical_with( new_frame_type):
                frame_type.reconnect_args( new_frame_type)
                frame_type.add_inst( new_frame_inst)
                break
        else:  # no identical frame was found
            self.frame_types.append( new_frame_type)

        return new_frame_inst

