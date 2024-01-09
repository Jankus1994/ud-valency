from eval_frame_extractor import Eval_frame_extractor, Extractor_record
from copy import deepcopy
from collections import defaultdict
from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor
from base_frame_extractor import Base_frame_extractor
from extraction_unit import Extraction_unit

class Exam_frame_extractor( Eval_frame_extractor):
    def __init__( self, lang_mark="", gold_name="", mist_name="",
                  output_form="text", output_name="", modals="",
                  exam_code="", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( lang_mark, gold_name, mist_name, output_form,
                          output_name, modals, **kwargs)

        if lang_mark == "cs":
            extractor_class = Cs_frame_extractor
        elif lang_mark == "en":
            extractor_class = En_frame_extractor
        else:
            extractor_class = Frame_extractor
        self.lang_mark = lang_mark

        full_extractor = extractor_class( lang_mark=lang_mark,
                                               output_form=output_form,
                                               output_name=output_name,
                                               modals=modals, **kwargs)
        #base_extractor = Base_frame_extractor( output_form=output_form,
        #                                output_name=output_name, **kwargs)

        base_extractor = extractor_class( lang_mark=lang_mark,
                                               output_form=output_form,
                                               output_name=output_name,
                                               modals=modals, **kwargs)


        plus_extractor = extractor_class( lang_mark=lang_mark,
                                               output_form=output_form,
                                               output_name=output_name,
                                               modals=modals, **kwargs)
        mnus_extractor = extractor_class( lang_mark=lang_mark,
                                               output_form=output_form,
                                               output_name=output_name,
                                               modals=modals, **kwargs)


        self.extres = {}
        self.extres[ "base" ] = Extractor_record( base_extractor, "BASE")
        self.extres[ "plus" ] = Extractor_record( plus_extractor, "PLUS")
        self.extres[ "mnus" ] = Extractor_record( mnus_extractor, "MNUS")
        self.extres[ "full" ] = Extractor_record( full_extractor, "FULL")






        self.sent_id = 0
        self.gold_sent_frames = self.read_gold_data( gold_name)
        self.mist_file = open( mist_name, 'w')

        self.exam_code = exam_code

    def before_process_document( self, doc):
        for extre in self.extres.values():
            extre.extractor.before_process_document( doc)
            extre.extractor.unit_dict[ "coun" ] = Extraction_unit( "coun", "", extre.extractor, False)

        for config_code in self.extres[ "full" ].extractor.unit_dict.keys():
            #if self.extres[ "plus" ].extractor.unit_dict[ config_code ].prename != self.lang_mark:
            #    continue
            self.extres[ "base" ].extractor.unit_dict[ config_code ] = \
                    Extraction_unit( config_code, self.lang_mark, self.extres[ "base" ].extractor, False)
            if config_code != self.exam_code:
                self.extres[ "plus" ].extractor.unit_dict[ config_code ] = \
                        Extraction_unit( config_code, self.lang_mark, self.extres[ "plus" ].extractor, False)
        # deactivation of all other mnus
        self.extres[ "mnus" ].extractor.unit_dict[ self.exam_code ] = \
                Extraction_unit( self.exam_code, self.lang_mark, self.extres[ "mnus" ].extractor, False)
        #plus_extractor.config_dict[ key ] = False

        #for extre in self.extres.values():
        #    print( { name:unit.active for name, unit in extre.extractor.unit_dict.items()})

        #del self.extres[ "mnus" ], self.extres[ "full" ]


    def process_tree( self, tree):  # -> list of Frame_inst
        self.sent_id += 1
        for extre in self.extres.values():
            extre_frame_insts = extre.extractor.process_tree( tree)
            if self.sent_id % 10 == 0:
                extre.sent_frame_insts.append( extre_frame_insts)
        #print( len( self.extres[ "base"].extractor.dict_of_verbs))
        #return []
        if self.sent_id % 10 == 0:
            #print("--")
            #for frame_inst in self.extres[ "plus" ].sent_frame_insts[ -1 ]:
            #    print( str( frame_inst))

            self.examine_diffs( self.extres[ "base" ].sent_frame_insts[ -1 ],
                                self.extres[ "plus" ].sent_frame_insts[ -1 ])
            #self.examine_diffs( self.extres[ "mnus" ].sent_frame_insts[ -1 ],
            #                    self.extres[ "full" ].sent_frame_insts[ -1 ])
        return []

    def examine_diffs( self, a_frame_insts, b_frame_insts):
        for a_frame_inst, b_frame_inst in zip( a_frame_insts, b_frame_insts):
            self.compare_frame_insts( a_frame_inst, b_frame_inst)

    @staticmethod
    def compare_frame_insts( a_frame_inst, b_frame_inst):
        if a_frame_inst.type.verb_lemma != b_frame_inst.type.verb_lemma:
            print( a_frame_inst.type.verb_lemma, b_frame_inst.type.verb_lemma)
            return
        if len( a_frame_inst.args) != len( b_frame_inst.args):
            print( "===")
            for a_arg in a_frame_inst.args:
                print( str( a_arg.type), a_arg.token.form)
            print( "--")
            for b_arg in b_frame_inst.args:
                print( str( b_arg.type), b_arg.token.form)
            print( "===")

    def after_process_document( self, doc):

        #print(self.extres[ "base" ].extractor.unit_dict)
        #print(self.extres[ "plus" ].extractor.unit_dict)

        names = [ "names" ]
        frm_id = "FRM_ID"
        lemmas = "LEMMAS"
        arg_id = "ARG_ID"
        argdsc = "ARGDSC"
        self.bare_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
                              arg_id: [ arg_id ], argdsc: [ argdsc ]}
        self.impr_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
                              arg_id: [ arg_id ], argdsc: [ argdsc ]}

        for extre in self.extres.values():
            names.append( extre.name)
            extre.extractor.after_process_document( doc)
            print( extre.name)
            extre.extractor.print_example_counts( self.exam_code)
            print( "---")
            sent_frames = self.get_extr_frames( extre.sent_frame_insts)
            extre.results = self.compare_sent_frames(
                    self.gold_sent_frames, sent_frames)

        self.compare_with_ref(self.extres["plus"].results,
                              self.extres[ "base" ].results)
        self.compare_with_ref(self.extres["full"].results,
                              self.extres[ "mnus" ].results)

        print( '\t'.join( names))

        print( '\t'.join( self.bare_results[ frm_id ]))
        print( '\t'.join( self.bare_results[ lemmas ]))
        print( '\t'.join( self.bare_results[ arg_id ]))
        print( '\t'.join( self.bare_results[ argdsc ]))

        print( '\t'.join( self.impr_results[ frm_id ]))
        print( '\t'.join( self.impr_results[ lemmas ]))
        print( '\t'.join( self.impr_results[ arg_id ]))
        print( '\t'.join( self.impr_results[ argdsc ]))


    def compare_with_ref(self, extr_results, base_results):
        #print( "===")
        #print( "IMPR")
        val_names = [ "FRM_ID", "LEMMAS", "ARG_ID", "ARGDSC" ]
        for extr_val, base_val, val_name in zip( extr_results, base_results, val_names):
            resid = 100 - base_val
            over = extr_val - base_val
            improve = 0
            if resid == 0 and over < 0:
                improve = "-INF"
            elif resid > 0:
                improve = round( 100 / resid * over, 2)
            #print( val_name + ": ", improve)
            self.impr_results[ val_name ].append( '- ')
            self.impr_results[ val_name ].append( str( improve))
