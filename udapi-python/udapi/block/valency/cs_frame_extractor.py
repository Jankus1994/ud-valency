from udapi.block.valency.frame_extractor import *
 
class Cs_frame_extractor( Frame_extractor):
    #def __init__( self, output = None, **kwargs):
    #    super().__init__( **kwargs)
    #    self.appropriate_udeprels = [ "nsubj", "csubj", "obj", "iobj", "ccomp", "xcomp", "expl" ]
    #    self.appropriate_deprels = [ "obl:arg", "obl:agent" ]
    #    self.dict_of_verbs = {}
    #    self.output = output

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
        
        frame.process_example_sentence( node, [ arg.example_node for arg in frame.arguments ])
        return frame

    def after_process_document( self, doc): # void
        self.delete_subframes() # reducing number of frames before outputting
        super().after_process_document( doc)

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
        if ( any( arg.is_identical_with( expl_arg) for arg in frame_args) and
                any( arg.is_identical_with( nsubj_arg) for arg in frame_args) ):
            frame_args = self.remove_arg( frame_args, expl_arg)
            frame_args = self.subst_arg( frame_args, nsubj_arg, obj_arg)
        return frame_args
    
    def subst_arg( self, frame_args, old_arg, new_arg): # -> list of transformed Frame_arguments
        """ substitution of old_arg with new_arg """
        return [ new_arg if arg.is_identical_with( old_arg) else arg for arg in frame_args ]
    def remove_arg( self, frame_args, rem_arg): # -> list of transformed Frame_arguments
        """ removing rem_arg from list of frame arguments """
        return [ arg for arg in frame_args if not arg.is_identical_with( rem_arg)]
