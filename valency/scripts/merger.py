"""
script to merge two conllu files that contain analogical sentences
in different languages. it creates bundles, that contains two corresponding
sentences, distinguished by language (zone) mark

"""
import sys

def process_sentence( file, zone_mark):
    was_sentence_text = False  # in case there were multiple empty lines
    sent_id = ""
    for line in file:
        line = line.rstrip( '\n')
        if line.startswith( "# sent_id = "):
            sent_id = line.lstrip( "# sent_id = ")
            was_sentence_text = True
            print( line + '/' + zone_mark)
        elif line != "":
            was_sentence_text = True
            print( line)
        else:
            print( line)
            if was_sentence_text:
                return sent_id
    return None


a_zone_mark = sys.argv[ 1 ]
a_file_name = sys.argv[ 2 ]
b_zone_mark = sys.argv[ 3 ]
b_file_name = sys.argv[ 4 ]

with open( a_file_name, 'r') as a_file, open( b_file_name, 'r') as b_file:
    while True:
        a_sent_id = process_sentence( a_file, a_zone_mark)
        b_sent_id = process_sentence( b_file, b_zone_mark)
        if a_sent_id is None and b_sent_id is None:
            break
        if a_sent_id is None or b_sent_id is None:
            print( "ERROR: one file ended", a_sent_id, b_sent_id, file=sys.stderr)
            exit()
        if a_sent_id != b_sent_id:
            print( "ERROR: different IDs", a_sent_id, b_sent_id, file=sys.stderr)
            exit()
