import sys, pickle

class Frame_examiner:
    def examine( self, dict_of_verbs):
        frames = []
        for verb_lemma in dict_of_verbs.keys():
            verb_record = dict_of_verbs[ verb_lemma ]
            for frame in verb_record.frames:
                verb_form = frame.verb_form
                voice = frame.voice
                arguments = frame.arguments_to_string()
                record = [ verb_lemma, verb_form, voice, arguments ]
                print( '\t'.join( record))



if ( len( sys.argv) == 2 ):
    fe = Frame_examiner()
    dict_of_verbs = pickle.load( open( sys.argv[ 1 ], "rb" ))
    fe.examine( dict_of_verbs)
