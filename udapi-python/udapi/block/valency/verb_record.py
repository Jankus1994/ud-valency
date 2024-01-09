from frame_type import Frame_type
from dag_fucntions import create_dag

class Verb_record:
    """ class representing one verb with possibly more verb frames """
    def __init__( self, lemma):
        """ called from Frame_extractor.process_node """
        self.lemma = lemma
        self._frame_types = []
        self._subframes = []

    @property
    def frame_types( self):
        return self._frame_types
    #@frame_types.setter
    #def frame_types( self, frame_types):
    #    self._frame_types = frame_types
    def add_frame( self, frame_type):
        self._frame_types.append( frame_type)
    def remove_frame( self, frame_type):
        self._frame_types.remove( frame_type)
    def sort_frames( self):
        self._frame_types.sort( key=lambda frame_type: len( frame_type.insts),
                                reverse=True)

    @property
    def subframes( self):
        return self._subframes
    def add_subframe( self, frame_type):
        self._subframes.append( frame_type)
    def remove_subframe( self, frame_type):
        self._subframes.remove( frame_type)
    def sort_subframes( self):
        for subframe in self.subframes:
            subframe.sort_subframes()
        self._subframes.sort( key=lambda subframe: subframe.tree_inst_num,
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
            if frame_type.agrees_with( new_frame_type) \
                    and frame_type is not new_frame_type:
                frame_type.reconnect_insts(new_frame_type)
                new_frame_type.deleted = True
                break
        else:  # no identical frame was found
            self.add_frame( new_frame_type)
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
            if frame_type.agrees_with( changed_frame_type):
                frame_type.reconnect_insts( changed_frame_type)
                self.remove_frame( changed_frame_type)
                changed_frame_type.deleted = True
                #changed_frame_type.verb_record = None  # VYMAZAT !!!
                #self.check_coherence()
                return True
        #self.check_coherence()
        return False

    # def find_frame_type( self, searched_frame_type):
    #     for frame_type in self.frame_types:
    #         if frame_type.agrees_with( searched_frame_type):
    #             return frame_type

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

    # def build_frame_tree( self):
    #     for frame_type in self.frame_types:
    #         frame_type.dive_into_frame_tree( self, 0)
    #     for frame_type in self.subframes:
    #         frame_type.superframe = None
    #         frame_type.set_additional_args()
    #         frame_type.sort_subframe_tree()
    #     self.sort_subframes()

    def build_frame_dag( self):
        dag_table = create_dag( self.frame_types, self.compare_frame_args)
        for i in range( len( self.frame_types)):
            for j in range( len( self.frame_types)):
                if i < j:
                    ij_relation = dag_table[ i ][ j ]
                    if ij_relation != 0:
                        i_frame_type = self.frame_types[ i ]
                        j_frame_type = self.frame_types[ j ]
                        if ij_relation == 1:
                            i_frame_type.add_subframe( j_frame_type)
                            j_frame_type.add_superframe( i_frame_type)
                        elif ij_relation == -1:
                            j_frame_type.add_subframe( i_frame_type)
                            i_frame_type.add_superframe( j_frame_type)
        for frame_type in self.frame_types:
            if frame_type.superframes == []:
                self.add_subframe( frame_type)
        self.sort_subframes()
        self.index_subframes()
        #else:
        #    frame_type.choose_tree_superframe( self)  # incl. inverse relation


    @staticmethod
    def compare_frame_args( a_frame_type, b_frame_type):
        """ whether ane of the frames is a superframe of the other
        i. e. whether their args form a super-/subset
         0: frames are not comparable
         1: A is superframe of B
        -1: B is superframe of A
        """
        if len( a_frame_type.args) < len( b_frame_type.args):
            if a_frame_type.should_be_superframe_of( b_frame_type):
                return 1
            return 0
        if len( a_frame_type.args) > len( b_frame_type.args):
            if b_frame_type.should_be_superframe_of( a_frame_type):
                return -1
            return 0
        # if len( self.args) == len( other_frame.args):
        # assumed all frames are in the record are distinct
        return 0

    def index_subframes( self):
        index = 1
        for subframe in self.subframes:
            index = subframe.index_subframes( index)

    def frame_reduction( self, reduction_coef):
        for frame in self.subframes:
            frame.try_reduce_subtrees( reduction_coef)


    def finalize_extraction( self, extraction_finalizer):
        """ called from Frame_aligner.after_process_document
        runs all extraction methods that need to look at whole dictionary
        not only individual records / frames / frame arguments
        universally used for oblique arguments
        may be used also for language-specific modifications
        """
        for frame_type in self.frame_types:
            frame_type.finalize_extraction( extraction_finalizer)

