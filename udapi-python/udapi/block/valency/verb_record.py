from frame_type import Frame_type

class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        """ called from Frame_extractor.process_node """
        self.lemma = lemma
        self.frame_types = []

    def consider_new_frame_type( self, new_frame_type): #, new_frame_inst):  # -> void
        """
        1 - called from Frame_extractor.process_frame
        gets a Frame_type and its (first) Frame_inst
        controls if this Frame_type is already present in the list and if yes,
        the new instance is only added to it
        2 - called from Extraction_finalizer.finalize_extraction
        similar situation, but the considered frame type is an old frame
        with one (or more) arg removed, so it is chcecked whether after the removal
        it is identical with anoter type. unlike new frames, a reduced frame
        can contain many instances
        it is necessary to ensure it is the same frame object
        otherwise the instances would be multiplied instead of reconnected
        """
        # comparing with already existing frames
        for frame_type in self.frame_types:
            if frame_type.is_identical_with( new_frame_type) \
                    and frame_type is not new_frame_type:
                frame_type.reconnect_args( new_frame_type)
                for frame_inst in new_frame_type.insts:
                    frame_type.add_inst( frame_inst)
                break
        else:  # no identical frame was found
            self.frame_types.append( new_frame_type)

        #return new_frame_inst

    def find_frame_type( self, searched_frame_type):
        for frame_type in self.frame_types:
            if frame_type.is_identical_with( searched_frame_type):
                return frame_type


    def finalize_extraction( self, extraction_finalizer):
        """ called from Frame_aligner.after_process_document
        runs all extraction methods that need to look at whole dictionary
        not only individual records / frames / frame arguments
        universally used for oblique arguments
        may be used also for language-specific modifications
        """
        for frame_type in self.frame_types:
            frame_type.finalize_extraction( extraction_finalizer)

