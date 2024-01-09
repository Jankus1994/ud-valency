import xml.etree.ElementTree as et

def get_id_lemmas( filename):
    tree = et.parse( filename)
    root = tree.getroot()
    words = root.findall( ".//word")
    frame_dict = {}
    for word in words:
        lemma = word.attrib[ "lemma" ]
        frames = word.findall( ".//frame")
        for frame in frames:
            frame_id = frame.attrib[ "id" ]
            frame_dict[ frame_id ] = lemma
    return frame_dict

found_id_pairs = []
tree = et.parse("frames_pairs.xml")
root = tree.getroot()
en_frames = root.findall(".//en_frame")
for en_frame in en_frames:
    en_id = en_frame.attrib["en_id"]
    frame_pairs = en_frame.findall(".//frame_pair")
    for frame_pair in frame_pairs:
        cs_id = frame_pair.attrib["cs_id"]
        slots = frame_pair.findall(".//slot")
        for slot in slots:
            en_act = slot.attrib["en_functor"] == "ACT"
            en_pat = slot.attrib["en_functor"] == "PAT"
            cs_act = slot.attrib["cs_functor"] == "ACT"
            cs_pat = slot.attrib["cs_functor"] == "PAT"
            if (en_act and cs_pat) or (en_pat and cs_act):
                found_id = en_id, cs_id
                found_id_pairs.append(found_id)


en_dict = get_id_lemmas( "vallex_en.xml")
cs_dict = get_id_lemmas( "vallex_cz.xml")


for en_id, cs_id in found_id_pairs:
    try:
        en_lemma = en_dict[ en_id ]
        cs_lemma = cs_dict[ cs_id ]
        print( en_lemma, cs_lemma)
    except:
        print( en_id, cs_id)
    
