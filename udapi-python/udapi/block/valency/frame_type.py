from sent_token import Sent_token


class Frame_type:
    """ class representing verb frame with information about the verb
    and with a list of its arguments
    """
    def __init__( self, deprel_order):
        """ called from Frame_extractor._process_frame """
        self.deprel_order = deprel_order

        self.verb_lemma = ""
        self.verb_form = "0"
        self.voice = "0"
        self._verb_record = None

        self._insts = []
        self._args = []

        self._superframes = []
        self._tree_superframe = None
        self._subframes = []
        self._tree_subframes = []
        self._tree_index = None

        self._additional_args = []
        self._tree_inst_num = None
        self._deleted = False
        #self.str_args = [] # filled with _args_to_string_list
        self.links = []  # objects pairing corresponding frames from two languages

        self.matched_frames = []  # TODO PROPERTY

    @property
    def verb_record( self):
        return self._verb_record
    @verb_record.setter
    def verb_record( self, verb_record):
        self._verb_record = verb_record
        #if not self in self.verb_record.frame_types:
        #    print( "tuu")

    @property
    def insts( self):  # -> list of Frame_insts
        return self._insts
    def add_inst( self, frame_inst):  # void
        """ called from Frame_extractor._process_args for the first instance
        called from Verb_frame.consider_new_frame_type for instances from identical frames
        """
        self._insts.append( frame_inst)
        frame_inst.type = self

    @property
    def args( self):  # -> list of frame_type_args
        """ called from another Frame_type._has_identical_args_with and
        reconnect_args and later also from Frame_type_link._link_args
        """
        return self._args
    @args.setter
    def args( self, args):  #void
        """ called from Extraction_finalizer.obl_handling
        when copying frame type in order to find the same one but without
        the oblique argument
        """
        self._args = args
    def add_arg( self, frame_type_arg):  # void
        """ called from Frame_extractor._process_args """
        self._args.append( frame_type_arg)
        frame_type_arg.frame_type = self
        self.sort_args()
    def remove_arg( self, frame_type_arg):
        """ only removes arg type, does not deal with its instances or verb record
        for complex removal use arg.delete and verb_record.consider merging instead
        """
        #self.verb_record.check_coherence()
        # TODO: co ked ich bude viac?
        self._args.remove( frame_type_arg)
        #self.verb_record.check_coherence()
        self.sort_args()

            #print( res)
        #return arg_to_remove

    def get_arg( self, deprel, form, case_mark_rels):
        return [ arg for arg in self.args
                 if arg.agrees_with_desc( deprel, form, case_mark_rels) ]

    # def includes_arg( self, searched_arg):
    #     """ called from Frame_extractor.search_one_verb_for_obl_arg
    #     and in language-specific extractors
    #     """
    #     return any( arg.is_identical_with( searched_arg) for arg in self.args)

    def sort_args( self):  # void
        """ called from Frame_extractor._process_frame after processing all args
        important for comparing arguments
        """
        sorted_args = []
        used_indices = []
        for deprel in self.deprel_order:
            for i, arg in enumerate( self.args):
                if i not in used_indices and arg.deprel.startswith( deprel):
                    sorted_args.append( arg)
                    used_indices.append( i)
        if len( used_indices) < len( self.args):
            for i, arg in enumerate( self.args):
                if i not in used_indices:
                    sorted_args.append( arg)

        self.args = sorted_args
        # TODO: maybe move the sorting to frame_arg
        #self._args = sorted( self._args, key =
        #        lambda arg :( arg.deprel, arg.case_feat, arg.case_mark_rels ))
        for i, arg in enumerate( self.args):
            arg.id = i + 1

    @property
    def superframes( self):  # -> Frame_type
        return self._superframes
    def add_superframe( self, superframe):
        self._superframes.append( superframe)

    @property
    def additional_args( self):
        return self._additional_args
    def set_additional_args( self):
        if self.superframe is not None:
            self._additional_args = []
            for self_arg in self.args:
                for super_arg in self.superframe.args:
                    if self_arg.agrees_with( super_arg):
                        break
                else:
                    self._additional_args.append( self_arg)
        for subframe in self.subframes:
            subframe.set_additional_args()

    @property
    def subframes( self):
        return self._subframes
    def add_subframe( self, subframe):
        self._subframes.append( subframe)
    def remove_subframe( self, subframe):
        self._subframes.remove( subframe)
    def sort_subframes( self):
        if self.tree_inst_num is not None:
            return self.tree_inst_num
        self.tree_inst_num = len( self.insts)
        for subframe in self.subframes:
            self.tree_inst_num += subframe.sort_subframes()
        self._subframes.sort( key=lambda subframe: subframe.tree_inst_num,
                              reverse=True)
        return self.tree_inst_num

    @property
    def tree_superframe( self):  # -> Frame_type
        return self._tree_superframe
    @tree_superframe.setter
    def tree_superframe( self, tree_superframe):
        self._tree_superframe = tree_superframe
        tree_superframe.add_tree_subframe( self)

    @property
    def tree_subframes( self):
        return self._tree_subframes
    def add_tree_subframe( self, tree_subframe):
        self._tree_subframes.append( tree_subframe)
    def remove_tree_subframe( self, subframe):
        self._tree_subframes.remove( subframe)

    @property
    def tree_inst_num( self):
        return self._tree_inst_num
    @tree_inst_num.setter
    def tree_inst_num( self, tree_inst_num):
        self._tree_inst_num = tree_inst_num

    @property
    def tree_index( self):
        return self._tree_index
    @tree_index.setter
    def tree_index( self, tree_index):
        self._tree_index = tree_index
    def index_subframes( self, index):
        if self.tree_index is not None:
            return index
        self.tree_index = index
        index += 1
        for subframe in self.subframes:
            index = subframe.index_subframes( index)
        return index

    @property
    def deleted( self):
        return self._deleted
    @deleted.setter
    def deleted( self, bool_val):
        self._deleted = bool_val
        if bool_val == True:
            for arg in self.args:
                arg.deleted = True

    def has_subject( self):
        for arg in self.args:
            if "nsubj" in arg.deprel or "csubj" in arg.deprel:
                return True
        return False
 
    # === frame extraction methods ===

    def set_verb_features( self, verb_node):  # void
        """ called from the Frame_extractor._process_frame right after creation"""
        self.verb_lemma = verb_node.lemma

        if verb_node.feats[ "VerbForm" ] != "":
            self.verb_form = verb_node.feats[ "VerbForm" ]

        if verb_node.feats[ "Voice" ] != "":
            self.voice = verb_node.feats[ "Voice" ]

    def add_matched_frame( self, matched_frame):
        self.matched_frames.append( matched_frame)

    def agrees_with( self, another_frame_type):  # -> bool
        """ called from Verb_record.consider_new_frame_type
        checks if this frame is identical with another frame
        """
        if self.verb_lemma == another_frame_type.verb_lemma and \
                self._agrees_in_args_with(another_frame_type):
                #self.verb_form == another_frame_type.verb_form and \
                #self.voice == another_frame_type.voice and \
                #self._has_identical_args_with( another_frame_type):
            return True
        return False

    def _agrees_in_args_with( self, other_frame_type):  # -> bool
        """ called from is_identical_with
        checks if this frame has identical arguments with another frame
        """
        other_args = other_frame_type.args
        if len( self.args) != len( other_args):
            return False            

        free_indices = [ True ] * len( other_args)
        for self_arg in self.args:
            for index, other_arg in enumerate( other_args):
                if free_indices[ index ] and self_arg.agrees_with( other_arg):
                    free_indices[ index ] = False
                    break
            else:
                return False
        return True
        # for i in range( len( self.args)):  # THIS IS NOT BIJECTION
        #     # TODO ensure the args are always sorted
        #     self_arg = self.args[ i ]
        #     other_arg = other_args[ i ]
        #     if not self_arg.agrees_with( other_arg):
        #         return False
        # return True

    # def is_strict_subframe_of( self, another_frame_type):  # -> bool
    #     """ used only in specific maodules ??? TODO """
    #     another_frame_type_args = another_frame_type.args
    #     if len( self.args) >= len( another_frame_type_args):
    #         return False
    #
    #     for self_arg in self.args:
    #         found_equivalent = False
    #         for another_frame_arg in another_frame_type_args:
    #             if self_arg.agrees_with( another_frame_arg):
    #                 found_equivalent = True
    #         if not found_equivalent:
    #             return False
    #     return True

    def reconnect_insts( self, other_frame_type):  # void
        """ called from Verb_record.consider_new_frame_type
        we suppose, that it has been tested that the frames are identical
        """
        assert len( self.args) == len( other_frame_type.args)
        for i, other_frame_type_arg in enumerate( other_frame_type.args):
            self_frame_type_arg = self.args[ i ]
            for frame_inst_arg in other_frame_type_arg.insts:
                self_frame_type_arg.add_inst( frame_inst_arg)  # incl reversed link
            other_frame_type_arg.deleted = True
        for frame_inst in other_frame_type.insts:
            self.add_inst( frame_inst)  # incl reversed link

    # def dive_into_frame_tree( self, superframe, depth):
    #     if len( self.args) == depth:
    #         self.superframe = superframe
    #         superframe.add_subframe( self)
    #         return
    #     considered_frames = superframe.subframes[ : ]
    #     for frame in considered_frames:
    #         linear_relation = self.compare_args_with( frame)
    #         # if linear_relation is None:
    #         #     continue
    #         if linear_relation == True:
    #             superframe.remove_subframe( frame)
    #             frame.superframe = self
    #             self.add_subframe( frame)
    #         elif linear_relation == False:
    #             self.dive_into_frame_tree( frame, len( frame.args))
    #             break
    #     else:
    #         self.superframe = superframe
    #         superframe.add_subframe( self)
    #
    # def compare_args_with( self, other_frame):
    #     """ whether ane of the frames is a superframe of the other
    #     i. e. whether their args form a super-/subset
    #     None  - frames are not comparable
    #     True  - self is a superframe of the other frame
    #     False - the other frame is a superframe of self
    #     """
    #     if len( self.args) < len( other_frame.args):
    #         if self.is_superframe_of( other_frame):
    #             return True
    #         return None
    #     if len( self.args) > len( other_frame.args):
    #         if other_frame.is_superframe_of( self):
    #             return False
    #         return None
    #     # if len( self.args) == len( other_frame.args):
    #     return None

    # === subframes and reduction methods ===

    def should_be_superframe_of( self, other_frame):
        free_indices = [ True ] * len(  other_frame.args)
        for self_arg in self.args:
            for i, other_arg in enumerate( other_frame.args):
                if free_indices[ i ] and self_arg.agrees_with( other_arg):
                    free_indices[ i ] = False
                    break
            else:
                # one of the self args was not found in the other frames args
                return False
        # all self args were found in the other frames args
        return True

    def choose_tree_superframe( self):
        if self.superframes:
            opt_value = 0
            opt_superframe = self.superframes[ 0 ]
            for superframe in self.superframes:
                superframe_value = self.compute_superframe_value( superframe)
                if superframe_value > opt_value:
                    opt_value = superframe_value
                    opt_superframe = superframe
            self.tree_superframe = opt_superframe

    def compute_superframe_value( self, superframe):
        """ method for choosing best superframe for tree structure
        there can be several methods, number of instances of whole
        subtree is used here """
        return superframe.tree_inst_num

    def try_reduce_subtrees( self, reduction_coef):
        should_try_reduciton = True
        while should_try_reduciton:
            should_try_reduciton = False
            tree_subframes_copy = self.tree_subframes.copy()
            for tree_subframe in tree_subframes_copy:
                if self.should_reduce( tree_subframe, reduction_coef):
                    should_try_reduciton = True
                    frames_to_reduce = tree_subframe.get_tree_subtree()
                    for frame_to_reduce in frames_to_reduce:
                        assert frame_to_reduce in self.verb_record.frame_types
                        self.absorb_frame( frame_to_reduce)
                        self.verb_record.remove_frame( frame_to_reduce)
                    self.remove_tree_subframe( tree_subframe)
        # recursive call on the subframes left
        for tree_subframe in self.tree_subframes:
            tree_subframe.try_reduce_subtrees( reduction_coef)

    def should_reduce( self, subframe, reduction_coef):
        result = len( self.insts) > reduction_coef * subframe.tree_inst_num
        return result

    def get_subtree( self):
        subtree = [ self ]
        for subframe in self.subframes:
            subtree += subframe.get_subtree()
        return subtree
    def get_tree_subtree( self):
        tree_subtree = [ self ]
        for tree_subframe in self.tree_subframes:
            tree_subtree += tree_subframe.get_tree_subtree()
        return tree_subtree

    def absorb_frame( self, other_frame):
        free_indices = [ True ] * len( other_frame.args)
        for self_arg in self.args:
            for index, other_arg in enumerate( other_frame.args):
                if free_indices[ index ] and self_arg.agrees_with( other_arg):
                    for inst in other_arg.insts:
                        self_arg.add_inst( inst)  # incl reversed link
                    free_indices[ index ] = False
                    break
            else:
                assert False  # each arg should be pairable
        args_to_delete = [ other_frame.args[ index ]
                           for index in range( len( other_frame.args))
                           if free_indices[ index ] ]
        for arg_to_delete in args_to_delete:
            arg_to_delete.delete()
        for frame_inst in other_frame.insts:
            self.add_inst( frame_inst)  # incl reversed link

    def try_delete_coord_args( self):
        """ deleting an arg, if all instances are from coord head
        it would be also possible to check the corresponding frame without
        the coord arg - if it exists, if it does not have another coord args etc.
        it is important to do the this coord deletion from the frames with many
        args to those with few args, so in the case of deletion and merging with
        another frame, the above frame could count with the instances of this frame
        """
        success = False
        for arg in self.args:
            if "subj" in arg.deprel:
                continue
            all_arg_inst_num = len( arg.insts)
            coord_arg_inst_num = len( [ arg_inst for arg_inst in arg.insts
                                        if arg_inst.is_coord_arg ])
            if all_arg_inst_num == coord_arg_inst_num:
                # all arg insts are taken only from coord head
                # this is probably not a true arg
                arg.delete()
                success = True
        return success


    # === ??? ===

    def finalize_extraction( self, extraction_finalizer):  # void
        """ called from Verb_record.finalize_extraction """
        for frame_type_arg in self.args:
            frame_type_arg.finalize_extraction( extraction_finalizer)

    # === frame linking methods ===

    def add_frame_type_link( self, frame_type_link):  # void
        """ called from Frame_type_link.__init__ """
        if frame_type_link not in self.links:
            #if frame_type_link:
            # !!! maybe we should control if the link includes this frame !!!
            self.links.append( frame_type_link)
    
    def find_link_with( self, translation_frame_type):  # -> Frame_type_link
        """ called from Frame_aligner._frame_alignment """
        for frame_type_link in self.links:
            if frame_type_link.links_type( translation_frame_type):
                return frame_type_link
        return None

    # === html displaying methods ===

    def _args_to_string_list( self):  # -> list of str
        """ called from args_to_one_string
        converts Frame_args to their string representation
        """
        str_args = []
        for arg in self.args:
            arg_string = arg.deprel + '-' + arg.form
            if arg.case_mark_rels != []:
                arg_string += '(' + ','.join( arg.case_mark_rels) + ')'
            str_args.append( arg_string)
        return str_args

    def args_to_one_string( self): # -> str
        """ called from Frame_extractor._print_raw_frames - not used
        and from HTML_creator.process_frame_type
        creates one long string of all frame arguments
        """
        str_args = self._args_to_string_list()
        final_string = ' '.join( str_args)
        return final_string


