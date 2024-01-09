from udapi.core.block import Block
from copy import deepcopy
from collections import defaultdict
import json
from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor
from base_frame_extractor import Base_frame_extractor
from extraction_unit import Extraction_unit
from error_record import Error_record


RESULT_NAMES = [ "FRM_ID", "LEMMAS", "ARG_ID", "ARGDSC" ]
FRM_ID = 0
LEMMAS = 1
ARG_ID = 2
ARGDSC = 3

ID = 0
LEMMA = 1
FUNC = 1
FORM = 2

class Eval_frame:
    def __init__( self):
        self.verb = None
        self.args = []

class Extractor_record:
    def __init__( self, extractor_class, lang_mark, name):
        self.name = name
        self.extractor = extractor_class( lang_mark=lang_mark)
        self.lang_mark = lang_mark
        self.sent_frame_insts = []
        self.results = {}


    def set_results( self, results):
        fr_id_perc, lemma_perc, arg_id_perc_avg, arg_desc_perc_avg = results
        self.results[ RESULT_NAMES[ FRM_ID ] ] = fr_id_perc
        self.results[ RESULT_NAMES[ LEMMAS ] ] = lemma_perc
        self.results[ RESULT_NAMES[ ARG_ID ] ] = arg_id_perc_avg
        self.results[ RESULT_NAMES[ ARGDSC ] ] = arg_desc_perc_avg


def read_gold_data( gold_name):
    sent_frames = []
    with open( gold_name, 'r') as gold_file:
        for line_id, line in enumerate( gold_file):
            frame_records_field, _ = line.split( '\t')
            frame_records = []
            if frame_records_field != "":
                frame_records = frame_records_field.split( ';')
            eval_frames = []
            for frame_record in frame_records:
                eval_frame = Eval_frame()
                frame_items = frame_record.split()
                for frame_item in frame_items:
                    token_id, item_desc = frame_item.split( '-', 1)
                    if item_desc.startswith( 'V'):
                        _, verb_lemma = item_desc.split( ':')
                        verb = token_id, verb_lemma
                        eval_frame.verb = verb
                    else:
                        arg_func, arg_form = item_desc.split( '-')
                        arg = token_id, arg_func, arg_form
                        eval_frame.args.append( arg)
                    #if ':' in token_id:
                eval_frames.append( eval_frame)
            sent_frames.append( eval_frames)
    return sent_frames

class Eval_frame_extractor( Block):
    def __init__( self, lang_mark="", gold_name="", mist_name="", exam_code="",
                  **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)

        self.arg_prc = defaultdict(int)
        self.arg_rec = defaultdict(int)
        self.obl_ok = defaultdict(int)

        self.exam_code = exam_code

        self.lang_mark = lang_mark
        if self.lang_mark == "cs":
            extractor_class = Cs_frame_extractor
        elif self.lang_mark == "en":
            extractor_class = En_frame_extractor
        else:
            extractor_class = Frame_extractor
        #extractor_class = Frame_extractor
        #self.extractor_class = extractor_class
        self.full_extr_rec = Extractor_record( extractor_class, lang_mark, "FULL")
        self.base_extr_rec = Extractor_record( extractor_class, lang_mark, "BASE")

        self.lang_unit_codes = extractor_class.proper_unit_codes

        self.exam_unit_codes = []
        if self.exam_code == "all":
            self.exam_unit_codes = self.lang_unit_codes
        elif self.exam_code:
            self.exam_unit_codes = [ self.exam_code ]


        self.plus_extr_recs, self.mnus_extr_recs = {}, {}
        self.unit_extr_rec_groups = {}
        for unit_code in self.exam_unit_codes:
            plus_extr_rec = Extractor_record( extractor_class, lang_mark, "P:"+unit_code)
            self.plus_extr_recs[ unit_code ] = plus_extr_rec
            mnus_extr_rec = Extractor_record( extractor_class, lang_mark, "M:"+unit_code)
            self.mnus_extr_recs[ unit_code ] = mnus_extr_rec

            unit_extr_rec_group = {}
            unit_extr_rec_group[ "base" ] = self.base_extr_rec
            unit_extr_rec_group[ "plus" ] = plus_extr_rec
            unit_extr_rec_group[ "mnus" ] = mnus_extr_rec
            unit_extr_rec_group[ "full" ] = self.full_extr_rec

            self.unit_extr_rec_groups[ unit_code ] = unit_extr_rec_group
        self.all_extr_recs = [ self.full_extr_rec, self.base_extr_rec ] +\
                list( self.plus_extr_recs.values()) + \
                list( self.mnus_extr_recs.values())

        # overit, ci sa pri variante mu skutocne overuje baselina
        # prejst si finalne unity, ci je vsetko ok
        # zistit, ci a preco su take rovnake vysledky
        #self.baseline = baseline_class( output_form=output_form,
        #                                output_name=output_name, **kwargs)
        # obmenit toto, aby  to slo spustat bez vyhodnotenia!


        self.sent_id = 0
        self.gold_sent_frames = read_gold_data( gold_name)
        self.mist_files = {}
        self.error_lists = {}
        for extr_rec in self.all_extr_recs:
            extr_mist_name = mist_name + extr_rec.name
            self.mist_files[ extr_rec.name ] = open( extr_mist_name, 'w')
            self.error_lists[ extr_rec.name ] = []
        self.act_mist_file = None
        self.act_error_list = None
        #self.act_mist_file = open( mist_name, 'w')

        # results
        self.names = []
        self.result_names = [ "FRM_ID", "LEMMAS", "ARG_ID", "ARGDSC" ]
        self.bare_results = {}
        self.impr_results = {}

    def before_process_document( self, doc):
        self.prepare_extractor( doc, self.full_extr_rec.extractor)
        self.prepare_extractor( doc, self.base_extr_rec.extractor)

        for unit_code in self.exam_unit_codes:
            self.prepare_extractor( doc, self.plus_extr_recs[ unit_code ].extractor)
            self.prepare_extractor( doc, self.mnus_extr_recs[ unit_code ].extractor)
            self.deactivate_unit( self.mnus_extr_recs[ unit_code ].extractor, unit_code)

        for lang_code in self.lang_unit_codes:
            self.deactivate_unit( self.base_extr_rec.extractor, lang_code)
            for exam_code in self.exam_unit_codes:
                if lang_code != exam_code:
                    self.deactivate_unit( self.plus_extr_recs[ exam_code ].extractor, lang_code)

        for extr_rec in self.all_extr_recs:
            extr_rec.extractor.after_config()

        #self.print_units()

    def print_units( self):
        #print(self.unit_extr_rec_groups.keys())
        for unit_code, group in self.unit_extr_rec_groups.items():
            for extr_rec in group.values():
                if ':' in extr_rec.name:  # PLUS, MINUS
                    print( ">>", extr_rec.name)
                    for examined_unit_code, unit in extr_rec.extractor.unit_dict.items():
                        print(examined_unit_code, unit.active, type(unit))
                        print(extr_rec.extractor.appropriate_udeprels)
                    print("=-=")
        for extr_rec in [ self.full_extr_rec, self.base_extr_rec ]:
            print( ">>", extr_rec.name)
            for unit_code, unit in extr_rec.extractor.unit_dict.items():
                print(unit_code, unit.active)
            print("=-=")
        #exit()

    def prepare_extractor( self, doc, extractor):
        extractor.process_config_file( self.lang_mark)
        #self.deactivate_unit( extractor, "coun")
        self.deactivate_unit( extractor, "outp")

    def deactivate_lang_units( self, extractor, lang_mark):
        for unit_code, unit in extractor.unit_dict.items():
            if unit.lang_mark == lang_mark:
                self.deactivate_unit( extractor, unit_code)

    def deactivate_unit( self, extractor, unit_code):
        # !!! inaksie poriesit deaktivaciu jednotiek
        extractor.unit_dict[ unit_code ] = \
                Extraction_unit( unit_code, "", extractor, False)

    # def clone_config_extractor( self):
    #     coun_unit = self.full_extractor.unit_dict["coun"]
    #     outp_unit = self.full_extractor.unit_dict["outp"]
    #     self.full_extractor.unit_dict["coun"] = \
    #             Extraction_unit( "coun", self.lang_mark, self, False)
    #     self.full_extractor.unit_dict["outp"] = \
    #             Extraction_unit( "coun", self.lang_mark, self, False)
    #     config_codes = list(self.full_extractor.unit_dict.keys())
    #     config_codes.remove( "coun")
    #     config_codes.remove( "outp")
    #     only_extrs = {}
    #     excl_extrs = {}
    #
    #     output_form = self.full_extractor.output_form
    #     output_name = self.full_extractor.output_name
    #
    #     for actual_config_code in config_codes:
    #         ext_only_copy = self.extractor_class( lang_mark=self.lang_mark,
    #                                               output_form=output_form,
    #                                               output_name=output_name,
    #                                               modals=False)
    #         ext_excl_copy = self.extractor_class( lang_mark=self.lang_mark,
    #                                               output_form=output_form,
    #                                               output_name=output_name,
    #                                               modals=False)
    #         for other_config_code in config_codes:
    #             if other_config_code == actual_config_code:
    #                 #ext_only_copy.unit_dict[ other_config_code] = True
    #                 ext_excl_copy.unit_dict[ other_config_code] = \
    #                         Extraction_unit( other_config_code, self.lang_mark,
    #                                          self, False)
    #             else:
    #                 ext_only_copy.unit_dict[ other_config_code] = \
    #                         Extraction_unit( other_config_code, self.lang_mark,
    #                                          self, False)
    #                 #ext_excl_copy.unit_dict[ other_config_code] = True
    #         only_extrs[ actual_config_code + "_only" ] = ext_only_copy
    #         excl_extrs[ actual_config_code + "_excl" ] = ext_excl_copy
    #
    #     self.full_extractor.unit_dict["coun"] = coun_unit
    #     self.full_extractor.unit_dict["outp"] = outp_unit
    #
    #     return only_extrs, excl_extrs

    def process_tree( self, tree):  # -> list of Frame_inst
        self.sent_id += 1

        for extr_rec in self.all_extr_recs:
            extr_rec_frame_insts = extr_rec.extractor.process_tree( tree)
            if self.sent_id % 10 == 0:
                extr_rec.sent_frame_insts.append( extr_rec_frame_insts)
        if self.sent_id % 10 == 0:
            print( self.sent_id)
            full_insts = self.full_extr_rec.sent_frame_insts[ -1 ]
            base_insts = self.base_extr_rec.sent_frame_insts[ -1 ]
            for unit_code in self.exam_unit_codes:
                plus_insts = self.plus_extr_recs[ unit_code ].sent_frame_insts[ -1 ]
                mnus_insts = self.mnus_extr_recs[ unit_code ].sent_frame_insts[ -1 ]
                #self.examine_diffs( base_insts, plus_insts)
                #self.examine_diffs( mnus_insts, full_insts)

        # base_frame_insts = self.baseline.process_tree( tree)
        # full_frame_insts = self.full_extractor.process_tree( tree)
        # if self.sent_id % 10 == 0:
        #     self.base_sent_frame_insts.append( base_frame_insts)
        #     self.full_sent_frame_insts.append( full_frame_insts)
        #
        # for code, extractor in self.plus_extractors.items():
        #     frame_insts = extractor.process_tree( tree)
        #     if self.sent_id % 10 == 0:
        #         self.only_sent_frame_insts[ code ].append( frame_insts)
        # for code, extractor in self.mnus_extractors.items():
        #     frame_insts = extractor.process_tree( tree)
        #     if self.sent_id % 10 == 0:
        #         self.excl_sent_frame_insts[ code ].append( frame_insts)

        return []

    # def compare_eval_frames( self, gold_eval_frames, extr_eval_frames, extr_rec):
    #     print( "======", file=self.mist_file)
    #     print( self.sent_id, file=self.mist_file)
    #
    #     extr_rec.rel_frames += len( gold_eval_frames)
    #     sel_frames += len( extr_eval_frames)
    #     unpaired_extr_indices = [ True ] * len( extr_eval_frames)
    #     for gold_eval_frame in gold_eval_frames:
    #         assert gold_eval_frame.verb is not None
    #         for j, extr_eval_frame in enumerate( extr_eval_frames):
    #             if gold_eval_frame.verb[ ID ] == extr_eval_frame.verb[ ID ]:
    #                 agr_frames += 1
    #                 max_lemma_points += 1
    #                 lemma_point, arg_id_perc, arg_desc_perc = \
    #                         self.compare_eval_frame(
    #                                 gold_eval_frame, extr_eval_frame)
    #                 assert lemma_point in [0, 1]
    #                 got_lemma_points += lemma_point
    #                 arg_id_perc_sum += arg_id_perc
    #                 arg_desc_perc_sum += arg_desc_perc
    #                 unpaired_extr_indices[ j ] = False
    #                 break
    #         else:
    #             print( ">>", gold_eval_frame.verb[ LEMMA ], file=self.mist_file)
    #     for j in range( len( extr_eval_frames)):
    #         if unpaired_extr_indices[ j ]:
    #             extr_eval_frame = extr_eval_frames[ j ]
    #             print( "<<", extr_eval_frame.verb[ LEMMA ], file=self.mist_file)

    def examine_diffs( self, a_frame_insts, b_frame_insts):
        for a_frame_inst, b_frame_inst in zip( a_frame_insts, b_frame_insts):
            if str( a_frame_inst) != str( b_frame_inst):
                print( str( a_frame_inst))
                print( str( b_frame_inst))
                print("----")
            self.compare_frame_insts( a_frame_inst, b_frame_inst)

    @staticmethod
    def compare_frame_insts( a_frame_inst, b_frame_inst):
        if a_frame_inst.type.verb_lemma != b_frame_inst.type.verb_lemma:
            print( a_frame_inst.type.verb_lemma, b_frame_inst.type.verb_lemma)
            return
        if len( a_frame_inst.args) != len( b_frame_inst.args):
            print( "===")
            for a_arg in a_frame_inst.args:
                print( str( a_arg.type), a_arg.token.form, a_arg.token.ord)
            print( "--")
            for b_arg in b_frame_inst.args:
                print( str( b_arg.type), b_arg.token.form, b_arg.token.ord)
            print( "===")
        else:
            for a_arg, b_arg in zip( a_frame_inst.args, b_frame_inst.args):
                a_tuple = str( a_arg.type), a_arg.token.form, a_arg.token.ord
                b_tuple = str( b_arg.type), b_arg.token.form, b_arg.token.ord
                if a_tuple != b_tuple:
                    print( a_tuple)
                    print( b_tuple)
                    print("--")

    def after_process_document( self, doc):
        self.names = [ "names" ]
        frm_id, lemmas, arg_id, argdsc = self.result_names
        self.bare_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
                              arg_id: [ arg_id ], argdsc: [ argdsc ]}
        self.impr_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
                              arg_id: [ arg_id ], argdsc: [ argdsc ]}

        self.process_extr_rec_results( doc, self.full_extr_rec)
        self.process_extr_rec_results( doc, self.base_extr_rec)

        if self.exam_unit_codes:
            self.compare_all_with_base( doc, self.base_extr_rec, "BASE",
                                        self.plus_extr_recs)
            self.compare_all_with_base( doc, self.full_extr_rec, "FULL",
                                        self.mnus_extr_recs, revert=True)
        else:
            self.compare_full_with_base()

        self.print_errors()

        print( '\t'.join( self.names))

        print( '\t'.join( self.bare_results[ frm_id ]))
        print( '\t'.join( self.bare_results[ lemmas ]))
        print( '\t'.join( self.bare_results[ arg_id ]))
        print( '\t'.join( self.bare_results[ argdsc ]))

        print( '\t'.join( self.impr_results[ frm_id ]))
        print( '\t'.join( self.impr_results[ lemmas ]))
        print( '\t'.join( self.impr_results[ arg_id ]))
        print( '\t'.join( self.impr_results[ argdsc ]))

        #print("arg prc", self.arg_prc)
        #print("arg rec", self.arg_rec)
        #print("obl ok", self.obl_ok)


    def process_extr_rec_results( self, doc, extr_rec):
        self.actual_extr_rec = extr_rec.name
        self.act_mist_file = self.mist_files[ extr_rec.name ]
        self.act_error_list = self.error_lists[ extr_rec.name ]

        extr_rec.extractor.after_process_document( doc)
        extr_rec.extractor.print_example_counts( extr_rec.name, self.exam_unit_codes)
        #print( extr_rec.name)
        #extr_rec.extractor.print_example_counts( self.exam_code)
        #print( "---")
        extr_sent_frames = self.get_extr_frames( extr_rec.sent_frame_insts)
        extr_rec_results = self.compare_sent_frames(
                self.gold_sent_frames, extr_sent_frames)
        extr_rec.set_results( extr_rec_results)

        # #fr_id_perc, lemma_perc, arg_id_perc_avg, arg_desc_perc_avg
        # #self.bare_results[ "FRM_ID" ].append( str( fr_id_perc))
        # #self.bare_results[ "LEMMAS" ].append( str( lemma_perc))
        # #self.bare_results[ "ARG_ID" ].append( str( arg_id_perc_avg))
        # #self.bare_results[ "ARGDSC" ].append( str( arg_desc_perc_avg))
        #
        # names = [ "names", "BASE" ]
        # frm_id = "FRM_ID"
        # lemmas = "LEMMAS"
        # arg_id = "ARG_ID"
        # argdsc = "ARGDSC"
        # self.bare_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
        #                       arg_id: [ arg_id ], argdsc: [ argdsc ]}
        # self.impr_results = { frm_id: [ frm_id, "-" ], lemmas: [ lemmas, "-" ],
        #                       arg_id: [ arg_id, "-" ], argdsc: [ argdsc, "-" ]}
        #
        # self.baseline.after_process_document( doc)
        # base_sent_frames = self.get_extr_frames( self.base_sent_frame_insts)
        # base_res = self.compare_sent_frames(
        #         self.gold_sent_frames, base_sent_frames)
        #
        # for code, extractor in self.plus_extractors.items():
        #     #print( "\n==========================\n")
        #     #print( ">>>", code, "<<<")
        #     names.append( code)
        #     extractor.after_process_document( doc)
        #     extr_sent_frames = self.get_extr_frames(
        #             self.only_sent_frame_insts[ code ])
        #     extr_res = self.compare_sent_frames(
        #             self.gold_sent_frames, extr_sent_frames)
        #     self.compare_with_base( extr_res, base_res)
        #
        # names.append( "FULL")
        # self.full_extractor.after_process_document( doc)
        # full_sent_frames = self.get_extr_frames( self.full_sent_frame_insts)
        # full_res = self.compare_sent_frames(
        #         self.gold_sent_frames, full_sent_frames)
        # for val in self.impr_results.values():
        #     val.append( '-')
        #
        # for code, extractor in self.mnus_extractors.items():
        #     #print( "\n==========================\n")
        #     #print( ">>>", code, "<<<")
        #     names.append( code)
        #     extractor.after_process_document( doc)
        #     extr_sent_frames = self.get_extr_frames(
        #             self.excl_sent_frame_insts[ code ])
        #     extr_res = self.compare_sent_frames(
        #             self.gold_sent_frames, extr_sent_frames)
        #     self.compare_with_base( full_res, extr_res)
        #
        #
        # print( '\t'.join( names))
        #
        # print( '\t'.join( self.bare_results[ frm_id ]))
        # print( '\t'.join( self.bare_results[ lemmas ]))
        # print( '\t'.join( self.bare_results[ arg_id ]))
        # print( '\t'.join( self.bare_results[ argdsc ]))
        #
        # print( '\t'.join( self.impr_results[ frm_id ]))
        # print( '\t'.join( self.impr_results[ lemmas ]))
        # print( '\t'.join( self.impr_results[ arg_id ]))
        # print( '\t'.join( self.impr_results[ argdsc ]))


    def get_extr_frames( self, sent_frame_insts):
        sent_frames = []
        for frame_insts in sent_frame_insts:
            eval_frames = []
            for frame_inst in frame_insts:
                eval_frame = self.inst_to_eval_frame( frame_inst)
                eval_frames.append( eval_frame)
            sent_frames.append( eval_frames)
        return sent_frames

    @staticmethod
    def inst_to_eval_frame( frame_inst):
        eval_frame = Eval_frame()

        verb_id = str( frame_inst.verb_node_ord)
        verb_lemma = frame_inst.type.verb_lemma
        verb = verb_id, verb_lemma
        eval_frame.verb = verb

        for frame_inst_arg in frame_inst.args:
            arg_id = str( frame_inst_arg.token.ord)
            if frame_inst_arg.token.is_elided():
                arg_id = '_'
            arg_func = frame_inst_arg.type.deprel
            arg_form = frame_inst_arg.type.form
            if frame_inst_arg.type.case_mark_rels != []:
                arg_form += '|' + ','.join( frame_inst_arg.type.case_mark_rels)
            arg = arg_id, arg_func, arg_form
            eval_frame.args.append( arg)

        return eval_frame

    def compare_sent_frames( self, gold_sent_frames, extr_sent_frames):
        assert len( gold_sent_frames) == len( extr_sent_frames)
        rel_frames = 0
        sel_frames = 0
        agr_frames = 0
        max_lemma_points = 0
        got_lemma_points = 0
        arg_id_perc_sum = 0
        arg_desc_perc_sum = 0
        i = 0
        zipped_sent_frames = zip( gold_sent_frames, extr_sent_frames)
        for gold_eval_frames, extr_eval_frames in zipped_sent_frames:
            i += 1
            #print( "======", file=self.act_mist_file)
            #print(i, file=self.act_mist_file)

            rel_frames += len( gold_eval_frames)
            sel_frames += len( extr_eval_frames)
            unpaired_extr_indices = [ True ] * len( extr_eval_frames)
            for gold_eval_frame in gold_eval_frames:
                assert gold_eval_frame.verb is not None
                for j, extr_eval_frame in enumerate( extr_eval_frames):
                    if gold_eval_frame.verb[ ID ] == extr_eval_frame.verb[ ID ]:
                        agr_frames += 1
                        max_lemma_points += 1
                        lemma_point, arg_id_perc, arg_desc_perc = \
                                self.compare_eval_frame(
                                        gold_eval_frame, extr_eval_frame, i)
                        assert lemma_point in [0, 1]
                        got_lemma_points += lemma_point
                        arg_id_perc_sum += arg_id_perc
                        arg_desc_perc_sum += arg_desc_perc
                        unpaired_extr_indices[ j ] = False
                        break
                else:
                    verb_lemma = gold_eval_frame.verb[ LEMMA ]
                    #print( ">>", verb_lemma, file=self.act_mist_file)
                    self.act_error_list.append( Error_record( i, "VRB_MISS", verb_lemma))
            for j in range( len( extr_eval_frames)):
                if unpaired_extr_indices[ j ]:
                    extr_eval_frame = extr_eval_frames[ j ]
                    verb_lemma = extr_eval_frame.verb[ LEMMA ]
                    #print( "<<", verb_lemma, file=self.act_mist_file)
                    self.act_error_list.append( Error_record( i, "VRB_RDUN", verb_lemma))

        if agr_frames == 0:
            fr_id_perc = 0.0
            lemma_perc = 0.0
            arg_id_perc_avg = 0.0
            arg_desc_perc_avg = 0.0
        else:
            fr_id_prc = agr_frames / sel_frames
            fr_id_rec = agr_frames / rel_frames
            fr_id_fsc = 2 * fr_id_prc * fr_id_rec / ( fr_id_prc + fr_id_rec )
            fr_id_perc = round( 100 * fr_id_fsc, 2)

            lemma_perc = round( 100 * got_lemma_points / max_lemma_points, 2)

            arg_id_perc_avg = round( arg_id_perc_sum / agr_frames, 2)
            arg_desc_perc_avg = round( arg_desc_perc_sum / agr_frames, 2)

        #print( sel_frames, rel_frames , agr_frames)
        #print( "===")
        #print( "FRM ID: ", fr_id_perc)
        #print( "LEMMAS: ", lemma_perc)
        #print( "ARG ID: ", arg_id_perc_avg)
        #print( "ARGDSC: ", arg_desc_perc_avg)

        return fr_id_perc, lemma_perc, arg_id_perc_avg, arg_desc_perc_avg

    def compare_eval_frame( self, gold_eval_frame, extr_eval_frame, sent_id):
        lemma_point = int( gold_eval_frame.verb[ LEMMA ]
                           == extr_eval_frame.verb[ LEMMA ])
        #print( "---", file=self.act_mist_file)
        lemma_rec = gold_eval_frame.verb[ LEMMA ]
        if not lemma_point:
            lemma_rec += " X " + extr_eval_frame.verb[ LEMMA ]
        #print(lemma_rec, file=self.act_mist_file)
        #print( "**", file=self.act_mist_file)
        arg_agree_num = 0
        max_arg_desc_points = 0
        got_arg_desc_points = 0
        unpaired_extr_indices = [ True ] * len( extr_eval_frame.args)
        for gold_arg in gold_eval_frame.args:
            for i, extr_arg in enumerate( extr_eval_frame.args):
                if gold_arg[ ID ] == extr_arg[ ID ]:
                    arg_agree_num += 1
                    max_arg_desc_points += 2
                    proto_points = int( gold_arg[ FUNC ] == extr_arg[ FUNC ])
                    proto_points += int( gold_arg[ FORM ] == extr_arg[ FORM ])
                    if gold_arg[ ID ] == '_' and proto_points < 2:
                        continue
                    unpaired_extr_indices[ i ] = False
                    got_arg_desc_points += proto_points
                    if proto_points < 2:
                        text = ' '.join( gold_arg) + " ~ " + ' '.join( extr_arg)
                        #print( text, file=self.act_mist_file)
                        text = lemma_rec + '\t' + text
                        if gold_arg[ FUNC ] != extr_arg[ FUNC ]:
                            self.act_error_list.append(
                                    Error_record( sent_id, "ARG_FUNC", text))
                        if gold_arg[ FORM ] != extr_arg[ FORM ]:
                            self.act_error_list.append(
                                    Error_record( sent_id, "ARG_FORM", text))
                    break
            else:
                text = ' '.join( gold_arg) + " ~ _"
                #print( text, file=self.act_mist_file)
                text = lemma_rec + '\t' + text
                self.act_error_list.append(
                        Error_record( sent_id, "ARG_MISS", text))
        #print( "**", file=self.act_mist_file)
        for i in range( len( extr_eval_frame.args)):
            if unpaired_extr_indices[ i ]:
                extr_arg = extr_eval_frame.args[ i ]
                text = "_ ~ " + ' '.join( extr_arg)
                #print( text, file=self.act_mist_file)
                text = lemma_rec + '\t' + text
                self.act_error_list.append(
                        Error_record( sent_id, "ARG_RDUN", text))

        rel_args = len( gold_eval_frame.args)
        sel_args = len( extr_eval_frame.args)
        agr_args = arg_agree_num
        if agr_args == 0:
            arg_id_perc = 0.0
            arg_desc_perc = 0.0
        else:
            arg_id_prc = agr_args / sel_args
            self.arg_prc[ self.actual_extr_rec] += arg_id_prc
            arg_id_rec = agr_args / rel_args
            self.arg_rec[ self.actual_extr_rec ] += arg_id_rec
            arg_id_fsc = 2 * arg_id_prc * arg_id_rec / ( arg_id_prc + arg_id_rec )
            arg_id_perc = 100 * arg_id_fsc

            arg_desc_perc = 100 * got_arg_desc_points / max_arg_desc_points

        return lemma_point, arg_id_perc, arg_desc_perc

    def compare_all_with_base( self, doc, reference_extr_rec, reference_name,
                               tested_extr_recs, revert=False):
        if not revert:  # BASE
           self.add_reference_results( reference_extr_rec, reference_name)

        for tested_extr_rec in tested_extr_recs.values():
            self.process_extr_rec_results( doc, tested_extr_rec)
            if revert:  # FULL
                impr_results = self.compare_with_ref( tested_extr_rec,
                                                      reference_extr_rec)
            else:  # BASE
                impr_results = self.compare_with_ref( reference_extr_rec,
                                                      tested_extr_rec)
            self.add_tested_results( tested_extr_rec, impr_results)

        if revert:  # FULL
           self.add_reference_results( reference_extr_rec, reference_name)

    def compare_full_with_base( self):
        self.add_reference_results( self.base_extr_rec, "BASE")
        impr_results = self.compare_with_ref( self.base_extr_rec, self.full_extr_rec)
        self.add_tested_results( self.full_extr_rec, impr_results)

    def add_reference_results( self, reference_extr_rec, reference_name):
        self.names.append( reference_name)
        for result_name in self.result_names:
            self.bare_results[ result_name ].append(
                    str( reference_extr_rec.results[ result_name ]))
            self.impr_results[ result_name ].append( '-')

    def add_tested_results( self, tested_extr_rec, impr_results):
        self.names.append( tested_extr_rec.name)
        for result_name in RESULT_NAMES:
            self.bare_results[ result_name ].append(
                    str( tested_extr_rec.results[ result_name ]))
            self.impr_results[ result_name ].append( str( impr_results[ result_name ]))

    def compare_with_ref( self, basic_extr_rec, improved_extr_rec):
        #print( "===")
        #print( "IMPR")

        basic_results = basic_extr_rec.results
        improved_results = improved_extr_rec.results

        impr_results = {}
        for result_name in self.result_names:
            resid = 100 - basic_results[ result_name ]
            over = improved_results[ result_name ] - basic_results[ result_name ]
            improve = 0
            if resid == 0 and over < 0:
                improve = "-INF"
            elif resid > 0:
                improve = round( 100 / resid * over, 2)
            #print( val_name + ": ", improve)
            impr_results[ result_name ] = improve
        return impr_results


        # else:
        #     unit = self.unit_dict[ exam_unit_name ]
        #     if unit.frm_example_counter:
        #         print( "\nframe insts:", frame_inst_count)
        #     for count_name, freq in unit.frm_example_counter.items():
        #         perc = round( freq / frame_inst_count * 100, 1)
        #         print( exam_unit_name + ':' + count_name, freq, perc)
        #
        #     if unit.arg_example_counter:
        #         print( "\narg insts:", arg_inst_count)
        #     for count_name, freq in unit.arg_example_counter.items():
        #         perc = round( freq / arg_inst_count * 100, 1)
        #         print( exam_unit_name + ':' + count_name, freq, perc)

    def print_errors( self):
        for extr_rec in self.all_extr_recs:
            mist_file = self.mist_files[ extr_rec.name ]
            error_list = self.error_lists[ extr_rec.name ]
            for error_record in error_list:
                error_record.log_error( mist_file)
            mist_file.close()