from udapi.core.block import Block
from copy import deepcopy
from collections import defaultdict
from frame_extractor import Frame_extractor
from cs_frame_extractor import Cs_frame_extractor
from en_frame_extractor import En_frame_extractor
from base_frame_extractor import Base_frame_extractor

class Eval_frame_extractor( Block):
    def __init__( self, lang_mark="", gold_name="", mist_name="",
                  output_form="text", output_name="", modals="", **kwargs):
        """ called from Frame_aligner.__init__ """
        super().__init__( **kwargs)
        extractor_class = Frame_extractor
        if lang_mark == "cs":
            extractor_class = Cs_frame_extractor
        elif lang_mark == "en":
            extractor_class = En_frame_extractor
        #extractor_class = Frame_extractor
        self.base_extractor = Base_frame_extractor( output_form=output_form,
                                                    output_name=output_name,
                                                    **kwargs)
        extractor = extractor_class( lang_mark=lang_mark,
                                     output_form=output_form,
                                     output_name=output_name,
                                     modals=modals, **kwargs)
        self.extractor_dict = self.clone_config_extractor( extractor)

        self.sent_id = 0
        self.gold_sent_frames = self.read_gold_data( gold_name)
        self.mist_file = open( mist_name, 'w')
        self.base_sent_frame_insts = []
        self.extr_sent_frame_insts = defaultdict( list)

    @staticmethod
    def clone_config_extractor( extractor):
        extractor.config_dict[ "coun" ] = False
        extractor.config_dict[ "outp" ] = False
        config_codes = list( extractor.config_dict.keys())
        config_codes.remove( "coun")
        config_codes.remove( "outp")
        extractor_dict = {}

        for actual_config_code in config_codes:
            ext_only_copy = deepcopy( extractor)
            ext_excl_copy = deepcopy( extractor)
            for other_config_code in config_codes:
                if other_config_code == actual_config_code:
                    ext_only_copy.config_dict[ other_config_code ] = True
                    ext_excl_copy.config_dict[ other_config_code ] = False
                else:
                    ext_only_copy.config_dict[ other_config_code ] = False
                    ext_excl_copy.config_dict[ other_config_code ] = True
            extractor_dict[ actual_config_code + "_only" ] = ext_only_copy
            extractor_dict[ actual_config_code + "_excl" ] = ext_excl_copy

        extractor.config_dict[ "coun" ] = True
        extractor.config_dict[ "outp" ] = True
        extractor_dict[ "full" ] = extractor
        return extractor_dict

    @staticmethod
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

    def process_tree( self, tree):  # -> list of Frame_inst
        self.sent_id += 1
        base_frame_insts = self.base_extractor.process_tree( tree)
        if self.sent_id % 10 == 0:
            self.base_sent_frame_insts.append( base_frame_insts)

        for code, extractor in self.extractor_dict.items():
            frame_insts = extractor.process_tree( tree)
            if self.sent_id % 10 == 0:
                self.extr_sent_frame_insts[ code ].append( frame_insts)

        return base_frame_insts

    def after_process_document( self, doc):
        names = [ "names", "BASE" ]
        frm_id = "FRM_ID"
        lemmas = "LEMMAS"
        arg_id = "ARG_ID"
        argdsc = "ARGDSC"
        self.bare_results = { frm_id: [ frm_id ], lemmas: [ lemmas ],
                              arg_id: [ arg_id ], argdsc: [ argdsc ]}
        self.impr_results = { frm_id: [ frm_id, "-" ], lemmas: [ lemmas, "-" ],
                              arg_id: [ arg_id, "-" ], argdsc: [ argdsc, "-" ]}

        self.base_extractor.after_process_document( doc)
        base_sent_frames = self.get_extr_frames( self.base_sent_frame_insts)
        base_res = self.compare_sent_frames(
                self.gold_sent_frames, base_sent_frames)


        for code, extractor in self.extractor_dict.items():
            #print( "\n==========================\n")
            #print( ">>>", code, "<<<")
            names.append( code)
            extractor.after_process_document( doc)
            extr_sent_frames = self.get_extr_frames(
                    self.extr_sent_frame_insts[ code ])
            extr_res = self.compare_sent_frames(
                    self.gold_sent_frames, extr_sent_frames)
            self.compare_with_base( extr_res, base_res)

        print( '\t'.join( names))

        print( '\t'.join( self.bare_results[ frm_id ]))
        print( '\t'.join( self.bare_results[ lemmas ]))
        print( '\t'.join( self.bare_results[ arg_id ]))
        print( '\t'.join( self.bare_results[ argdsc ]))

        print( '\t'.join( self.impr_results[ frm_id ]))
        print( '\t'.join( self.impr_results[ lemmas ]))
        print( '\t'.join( self.impr_results[ arg_id ]))
        print( '\t'.join( self.impr_results[ argdsc ]))


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
        zipped_sent_frames = zip( gold_sent_frames, extr_sent_frames)
        rel_frames = 0
        sel_frames = 0
        agr_frames = 0
        max_lemma_points = 0
        got_lemma_points = 0
        arg_id_perc_sum = 0
        arg_desc_perc_sum = 0
        i = 0
        for gold_eval_frames, extr_eval_frames in zipped_sent_frames:
            i += 1
            print( "======", file=self.mist_file)
            print( i, file=self.mist_file)

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
                                        gold_eval_frame, extr_eval_frame)
                        assert lemma_point in [0, 1]
                        got_lemma_points += lemma_point
                        arg_id_perc_sum += arg_id_perc
                        arg_desc_perc_sum += arg_desc_perc
                        unpaired_extr_indices[ j ] = False
                        break
                else:
                    print( ">>", gold_eval_frame.verb[ LEMMA ], file=self.mist_file)
            for j in range( len( extr_eval_frames)):
                if unpaired_extr_indices[ j ]:
                    extr_eval_frame = extr_eval_frames[ j ]
                    print( "<<", extr_eval_frame.verb[ LEMMA ], file=self.mist_file)

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
        self.bare_results[ "FRM_ID" ].append( str( fr_id_perc))
        self.bare_results[ "LEMMAS" ].append( str( lemma_perc))
        self.bare_results[ "ARG_ID" ].append( str( arg_id_perc_avg))
        self.bare_results[ "ARGDSC" ].append( str( arg_desc_perc_avg))
        return fr_id_perc, lemma_perc, arg_id_perc_avg, arg_desc_perc_avg

    def compare_eval_frame( self, gold_eval_frame, extr_eval_frame):
        lemma_point = int( gold_eval_frame.verb[ LEMMA ]
                           == extr_eval_frame.verb[ LEMMA ])
        print( "---", file=self.mist_file)
        lemma_rec = gold_eval_frame.verb[ LEMMA ]
        if not lemma_point:
            lemma_rec += " X " + extr_eval_frame.verb[ LEMMA ]
        print( lemma_rec, file=self.mist_file)
        print( "**", file=self.mist_file)
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
                        print( ' '.join( gold_arg),
                               ' '.join( extr_arg), file=self.mist_file)
                    break
            else:
                print( ' '.join( gold_arg), file=self.mist_file)
        print( "**", file=self.mist_file)
        for i in range( len( extr_eval_frame.args)):
            if unpaired_extr_indices[ i ]:
                extr_arg = extr_eval_frame.args[ i ]
                print( ' '.join( extr_arg), file=self.mist_file)

        rel_args = len( gold_eval_frame.args)
        sel_args = len( extr_eval_frame.args)
        agr_args = arg_agree_num
        if agr_args == 0:
            arg_id_perc = 0.0
            arg_desc_perc = 0.0
        else:
            arg_id_prc = agr_args / sel_args
            arg_id_rec = agr_args / rel_args
            arg_id_fsc = 2 * arg_id_prc * arg_id_rec / ( arg_id_prc + arg_id_rec )
            arg_id_perc = 100 * arg_id_fsc

            arg_desc_perc = 100 * got_arg_desc_points / max_arg_desc_points

        return lemma_point, arg_id_perc, arg_desc_perc

    def compare_with_base( self, extr_results, base_results):
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
            self.impr_results[ val_name ].append( str( improve))

ID = 0
LEMMA = 1
FUNC = 1
FORM = 2

class Eval_frame:
    def __init__( self):
        self.verb = None
        self.args = []