from udapi.block.valency.frame_extractor import *
 
class Cs_frame_extractor( Frame_extractor):
    #def __init__( self, output = None, **kwargs):
    #    super().__init__( **kwargs)
    #    self.appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
    #    self.appropriate_deprels = [ "obl:arg", "obl:agent" ]
    #    self.dict_of_verbs = {}
    #    self.output = output

    def create_argument( self, node):  # -> Frame_argument
        is_numerative, original_case = self.consider_numerative( node)
        argument = super().create_argument( node)
        if is_numerative:
            argument.case_feat = original_case
        return argument

    def select_arguments( self, node): # -> list of Frame_arguments
        """ iterates through verb children and calls create_argument for each of them """
        #frame_arguments = []
        #for child in node.children:
        #    if ( child.udeprel in self.appropriate_udeprels or
        #            child.deprel in self.appropriate_deprels ):
        #        argument = self.create_argument( child)
        #        frame_arguments.append( argument)
        frame_arguments = super().select_arguments( node)
        frame_arguments = self.transform_reflex_passive( frame_arguments)
        return frame_arguments

    def create_frame( self, node): # -> Frame
        """ creates a verb frame for a given verb node """
        frame = Frame( node)
        # not setting verb form and voice !!! IS IT OK ? !!!

        frame_arguments = self.select_arguments( node)
        for argument in frame_arguments:
            frame.add_argument( argument)

        elided_pronoun = self.consider_elided_subject( node, frame_arguments)
        elided_tokens = []
        if elided_pronoun is not None:
            elided_argument, elided_token = elided_pronoun
            frame.add_argument( elided_argument)
            elided_tokens = [ elided_token ]
        elif not self.args_include_subject( frame_arguments):
            subject_arg = Frame_argument( "nsubj", "Nom", [], None)
            frame.add_argument( subject_arg)

        frame.process_example_sentence( node, [ arg.example_node for arg in frame.arguments ], elided_tokens)
        return frame

    def after_process_document( self, doc): # void
        self.delete_subframes() # reducing number of frames before outputting
        super().after_process_document( doc)

    def process_tree( self, tree):
        print( "CS", len( tree.descendants))
        super().process_tree( tree)
        #Frame_extractor.process_tree( self, tree)

    # ========== PROPER METHODS  ===========

    def delete_subframes( self): # void
        """ deleting frames, arguments of which form a subset of arguments
        another frame and have low frequency
        frequency and examples of these frames are added to their "superframe"
        """
        verb_lemmas = self.dict_of_verbs.keys()
        for verb_lemma in verb_lemmas:
            verb_record = self.dict_of_verbs[ verb_lemma ]
            frames = sorted( verb_record.frames, key = lambda arg:len( arg.str_arguments))
            # comparing frames and marking those to delete
            for frame in frames:
                frame.args_to_one_string()
            for frame in frames:
                # a frame should be deleted if it has a superframe
                superframes = [ other_frame for other_frame in frames
                                if ( set( frame.str_arguments).issubset( set( other_frame.str_arguments)) and
                                    len( frame.str_arguments) < len( other_frame.str_arguments) ) ]
                if ( superframes ):
                    # !!! we take the biggest (ie. last) superframe - IS IT CORRECT ??? !!!
                    # we mark the superframe only if the subframe has a low frequency compared to the superframe
                    if ( self.compare_frame_freqs( frame, superframes[ -1 ]) ):
                        frame.superframe = superframes[ -1 ]

            # building a reduced frame list
            reduced_frames = []
            for frame in frames:
                if ( frame.superframe is None ):
                    reduced_frames.append( frame)
                else:
                    # adding examples and frequency of the deleted frame to its superframe
                    for example_sent in frame.example_sentences:
                        frame.superframe.add_frame_instance( example_sent)
            verb_record.frames = reduced_frames

    def compare_frame_freqs( self, subframe, superframe): # -> bool
        """ comparing frequency of a subframe and a superframe
        returns if the superframe is sufficiently more frequent than the subframe
        """
        coef = 2 # !!!
        if ( coef * subframe.frequency < superframe.frequency ):
            return True
        return False


    def transform_reflex_passive( self, frame_args): # -> list of transformed Frame_arguments
        """ tranforming frames with reflexive passive construction to their active equivalent
        zahrada se kosi -> kosi zahradu
        expl:pass-Acc -> 0, nsubj:pass-Nom -> obj-Acc
        """
        expl_arg = Frame_argument( "expl:pass", "Acc", [], None)
        nsubj_arg = Frame_argument( "nsubj:pass", "Nom", [], None)
        obj_arg = Frame_argument( "obj", "Acc", [], None)
        if any( arg.is_identical_with( expl_arg) for arg in frame_args) and\
                any( arg.is_identical_with( nsubj_arg) for arg in frame_args):
            frame_args = self.remove_arg( frame_args, expl_arg)
            frame_args = self.subst_arg( frame_args, nsubj_arg, obj_arg)
        return frame_args

    def subst_arg( self, frame_args, old_arg, new_arg): # -> list of transformed Frame_arguments
        """ substitution of old_arg with new_arg """
        return [ new_arg if arg.is_identical_with( old_arg) else arg for arg in frame_args ]
    def remove_arg( self, frame_args, rem_arg): # -> list of transformed Frame_arguments
        """ removing rem_arg from list of frame arguments """
        return [ arg for arg in frame_args if not arg.is_identical_with( rem_arg) ]


    def consider_elided_subject( self, node, frame_args):
        for frame_arg in frame_args:
            if frame_arg.deprel == "nsubj" or frame_arg.deprel == "csubj":
                return None

        # the verb (node) does not have a subject:
        token_person_1_2 = self.get_token_of_person_1_2( node)
        if token_person_1_2 is not None:
            elided_argument = Frame_argument("nsubj", "Nom", [], None)
            elided_arg_token = ( elided_argument, token_person_1_2 )
            return elided_arg_token

        # looking for an auxiliary verb, which would confirm the 1./2. person
        for child in node.children:
            if child.upos == "AUX":
                token_person_1_2 = self.get_token_of_person_1_2( child)
                if token_person_1_2 is not None:
                    elided_argument = Frame_argument( "nsubj", "Nom", [], None)
                    elided_arg_token = ( elided_argument, token_person_1_2 )
                    return elided_arg_token

        # the node can be a complement of a parant verb, which could confirm the 1./2. person
        if node.deprel == "xcomp" and node.parent.upos == "VERB":
            token_person_1_2 = self.get_token_of_person_1_2( node.parent)
            if token_person_1_2 is not None:
                elided_argument = Frame_argument( "nsubj", "Nom", [], None)
                elided_arg_token = ( elided_argument, token_person_1_2 )
                return elided_arg_token

        return None

    def get_token_of_person_1_2( self, node):
        token = None
        if node.feats["Person"] == "1":
            if node.feats["Number"] == "Sing":
                token = "já"
            elif node.feats["Number"] == "Plur":
                token = "my"
        elif node.feats["Person"] == "2":
            if node.feats["Number"] == "Sing":
                token = "ty"
            elif node.feats["Number"] == "Plur":
                token = "vy"
        return token


    def args_include_subject( self, frame_args):
        for frame_arg in frame_args:
            if "nsubj" in frame_arg.deprel or "csubj" in frame_arg.deprel:
                return True
        return False


    def consider_numerative( self, node):
        original_case = ""
        for child in node.children:
            if child.deprel in [ "nummod:gov", "det:numgov" ]:
                original_case = child.feats[ "Case" ]
                return True, original_case
        return False, original_case

