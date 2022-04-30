import sys, pickle
import xml.etree.ElementTree as et
from enum import IntEnum

class Pair( IntEnum):
    CS = 0
    EN = 1



def get_val_frame_pairs( cs_id_val_frame_dict, en_id_val_frame_dict, align_filename):
    cs_en_val_frame_pairs = []

    tree = et.ElementTree( file=align_filename)
    root = tree.getroot()
    en_frame_elems = root.findall( ".//en_frame")
    for en_frame_elem in en_frame_elems:
        en_frame_id = en_frame_elem.attrib[ "en_id" ]
        en_frame = en_id_val_frame_dict[ en_frame_id ]
        frame_pairs = en_frame_elem.findall( "frame_pair")
        for frame_pair in frame_pairs:
            cs_frame_id = frame_pair.attrib[ "cs_id" ]
            cs_frame = cs_id_val_frame_dict[ cs_frame_id ]
            frame_pair = ( cs_frame, en_frame )
            cs_en_val_frame_pairs.append( frame_pair)

            ## slots
            #slots = frame_pair.findall( ".//slot")
            #cs_en_functor_pairs = []
            #for slot in slots:
            #    functor_pair = Functor_pair()
            #    functor_pair.cs_functor = slot.attrib[ "cs_functor" ]
            #    functor_pair.en_functor = slot.attrib[ "en_functor" ]
            #    cs_en_functor_pairs.append( functor_pair)

            #join_frames( cs_frame, en_frame, cs_en_functor_pairs)

    return cs_en_val_frame_pairs

def evaluate( cs_en_ext_dict, en_cs_ext_dict, cs_en_val_frame_pairs):
    gold_ext_frame_pairs = []
    auto_ext_frame_pairs = []

    #print( "cs-en val pairs: ", len( cs_en_val_frame_pairs))
    #cs_val_fr_num = 0
    #en_val_fr_num = 0
    #g_cs_ext_fr_num = 0
    #g_en_ext_fr_num = 0
    #g_ext_fr_pairs = 0
    for cs_en_val_frame_pair in cs_en_val_frame_pairs:
        cs_val_frame = cs_en_val_frame_pair[ Pair.CS ]
        en_val_frame = cs_en_val_frame_pair[ Pair.EN ]
        #if not hasattr( cs_val_frame, "visited"):
        #    cs_val_frame.visited = True
        #    cs_val_fr_num += 1
        #if not hasattr( en_val_frame, "visited"):
        #    en_val_frame.visited = True
        #    en_val_fr_num += 1

        for cs_ext_frame in cs_val_frame.matched_ext_frames:
            for en_ext_frame in en_val_frame.matched_ext_frames:
                #if not hasattr( cs_ext_frame, "visited"):
                #    cs_ext_frame.visited = True
                #    g_cs_ext_fr_num += 1
                #if not hasattr( en_ext_frame, "visited"):
                #    en_ext_frame.visited = True
                #    g_en_ext_fr_num += 1
                #g_ext_fr_pairs += 1
                gold_ext_frame_pair = ( cs_ext_frame, en_ext_frame )
                #gold_ext_frame_pairs.append( cs_ext_frame.verb_lemma )
                gold_ext_frame_pairs.append( gold_ext_frame_pair)


    #for en_verb_record in en_cs_ext_dict.values():
    #    for en_frame_type in en_verb_record.frame_types:
    #        en_frame_type.spam = True

    #a_cs_total = 0
    #a_cs_visit = 0
    #a_en_spam = 0
    #a_en_subtotal = 0
    #a_en_visit = 0
    #a_en_qyx = 0
    for cs_verb_record in cs_en_ext_dict.values():
        for cs_frame_type in cs_verb_record.frame_types:
            #if not hasattr( cs_frame_type, "total"):
            #    cs_frame_type.total = True
            #    a_cs_total += 1
            #if hasattr( cs_frame_type, "visited") and cs_frame_type.visited:
            #    a_cs_visit += 1
            #    cs_frame_type.visited = False
            for cs_en_frame_type_link in cs_frame_type.links:
                en_frame_type = cs_en_frame_type_link.get_the_other_frame_type( \
                                    cs_frame_type)
                #if not hasattr( en_frame_type, "subtotal"):
                #    en_frame_type.subtotal = True
                #    a_en_subtotal += 1
                #if hasattr( en_frame_type, "visited") and en_frame_type.visited:
                #    a_en_visit += 1
                #    en_frame_type.visited = False
                #if hasattr( en_frame_type, "spam") and en_frame_type.spam:
                #    a_en_spam += 1
                #    en_frame_type.spam = False


    #for en_verb_record in en_cs_ext_dict.values():
    #    for en_frame_type in en_verb_record.frame_types:
    #        if hasattr( en_frame_type, "subtotal"):
    #           a_en_qyx  += 1

    #print( "g_ext_fr_pairs", g_ext_fr_pairs)
    #print( "g_cs_ext_fr_num", g_cs_ext_fr_num)
    #print( "g_en_ext_fr_num", g_en_ext_fr_num)
    #print( "a_cs_total", a_cs_total)
    #print( "a_cs_visit", a_cs_visit)
    #print( "a_en_spam", a_en_spam)
    #print( "a_en_subtotal", a_en_subtotal)
    #print( "a_en_visit", a_en_visit)
    #print( "a_en_qyx", a_en_qyx)


                auto_ext_frame_pair = ( cs_frame_type, en_frame_type )
                #auto_ext_frame_pairs.append( cs_frame_type )
                auto_ext_frame_pairs.append( auto_ext_frame_pair)



    print( "Number of gold   frame pairs: ", len( gold_ext_frame_pairs))
    print( "Number of auto   frame pairs: ", len( auto_ext_frame_pairs))
    common_frame_pairs = list( set( gold_ext_frame_pairs) & set( auto_ext_frame_pairs))
    print( "Number of common frame pairs: ", len( common_frame_pairs))
    precis = 100 * len( common_frame_pairs) / len( auto_ext_frame_pairs)
    recall = 100 * len( common_frame_pairs) / len( gold_ext_frame_pairs)
    print( "Precision: ", precis)
    print( "Recall:    ", recall)
    #print( "gold visited", gold_visited)
    #print( "auto visited", auto_visited)

if __name__ == "__main__":
    if len( sys.argv) == 3:
        align_filename = sys.argv[ 1 ]
        matched_dicts_filename = sys.argv[ 2 ]

        matched_dicts = pickle.load( open( matched_dicts_filename, "rb" ))

        cs_en_ext_dict, cs_val_dict, en_cs_ext_dict, en_val_dict = matched_dicts

        cs_en_val_frame_pairs = get_val_frame_pairs( \
                cs_val_dict, en_val_dict, align_filename)

        evaluate( cs_en_ext_dict, en_cs_ext_dict, cs_en_val_frame_pairs)

