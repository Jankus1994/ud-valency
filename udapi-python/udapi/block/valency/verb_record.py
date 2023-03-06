from frame_type import Frame_type

class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        """ called from Frame_extractor.process_node """
        self.lemma = lemma
        self._frame_types = []

    @property
    def frame_types( self):
        return self._frame_types
    #@frame_types.setter
    #def frame_types( self, frame_types):
    #    self._frame_types = frame_types
    def _add_frame( self, frame_type):
        self._frame_types.append( frame_type)
    def _remove_frame( self, frame_type):
        self._frame_types.remove( frame_type)
    def sort_frames( self):
        self._frame_types.sort( key=lambda frame_type: len( frame_type.insts),
                               reverse=True)

    def consider_new_frame_type( self, new_frame_type): #, new_frame_inst):  # -> void
        """
        1 - called from Frame_extractor.process_frame
        gets a Frame_type and its (first) Frame_inst
        controls if this Frame_type is already present in the list and if yes,
        the new instance is only added to it
        2 - called from Extraction_finalizer.finalize_extraction
        similar situation, but the considered frame type is an old frame
        with one (or more) arg removed, so it is checked whether after the removal
        it is identical with another type. unlike new frames, a reduced frame
        can contain many instances
        it is necessary to ensure it is the same frame object
        otherwise the instances would be multiplied instead of reconnected
        """
        #self.check_coherence()
        if new_frame_type is None:
            return  # for cases of language specific deletion of the frame

        # comparing with already existing frames
        for frame_type in self.frame_types:
            if frame_type.is_identical_with( new_frame_type) \
                    and frame_type is not new_frame_type:
                #self.check_coherence()
                frame_type.reconnect_args( new_frame_type)
                #self.check_coherence()
                for frame_inst in new_frame_type.insts:
                    frame_type.add_inst( frame_inst)
                new_frame_type.deleted = True
                break
        else:  # no identical frame was found
            self._add_frame( new_frame_type)
            new_frame_type.verb_record = self
        #self.check_coherence()

        #return new_frame_inst

    def consider_merging( self, changed_frame_type):
        """ run after a fram of this record has changed """
        assert changed_frame_type in self.frame_types
        #self.check_coherence()
        # comparing with already existing frames
        for frame_type in self.frame_types:
            if frame_type is changed_frame_type:
                continue
            if frame_type.is_identical_with( changed_frame_type):
                #self.check_coherence()
                frame_type.reconnect_args( changed_frame_type)
                #self.check_coherence()
                for frame_inst in changed_frame_type.insts:
                    frame_type.add_inst( frame_inst)
                self._remove_frame( changed_frame_type)
                changed_frame_type.deleted = True
                changed_frame_type.verb_record = None  # VYMAZAT !!!
                #self.check_coherence()
                return True
        #self.check_coherence()
        return False

    def find_frame_type( self, searched_frame_type):
        for frame_type in self.frame_types:
            if frame_type.is_identical_with( searched_frame_type):
                return frame_type

    def check_coherence( self):
        for frame_type in self.frame_types:
            a_set = set()
            assert frame_type.verb_record is self
            for arg in frame_type.args:
                assert arg.frame_type is frame_type
                for arg_inst in arg.insts:
                    a_set.add( arg_inst)
                    assert arg_inst.type is arg
                    frame_inst = arg_inst.frame_inst
                    assert frame_inst is not None
                    assert arg_inst in frame_inst.args
            b_set = set()
            for frame_inst in frame_type.insts:
                assert frame_inst.type is frame_type
                for frame_inst_arg in frame_inst.args:
                    b_set.add( frame_inst_arg)
                    assert frame_inst_arg.frame_inst is frame_inst
                    arg_type = frame_inst_arg.type
                    assert arg_type is not None
                    assert frame_inst_arg in arg_type.insts
                    sent_token = frame_inst_arg.token
                    assert sent_token is not None
                    assert sent_token.arg is frame_inst_arg
                    assert sent_token in frame_inst.sent_tokens or \
                            sent_token in frame_inst.elided_tokens
            assert a_set == b_set

    def finalize_extraction( self, extraction_finalizer):
        """ called from Frame_aligner.after_process_document
        runs all extraction methods that need to look at whole dictionary
        not only individual records / frames / frame arguments
        universally used for oblique arguments
        may be used also for language-specific modifications
        """
        for frame_type in self.frame_types:
            frame_type.finalize_extraction( extraction_finalizer)

