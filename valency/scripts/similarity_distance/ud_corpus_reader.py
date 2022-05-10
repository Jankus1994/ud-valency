from collections import defaultdict

def extract_verb_lemmas( corpus_file_name):
    verb_dict = defaultdict(int)
    with open( corpus_file_name, 'r', encoding="utf8") as corpus_file:
        for line in corpus_file:
            line = line.rstrip( '\n')
            if line != "" and line[ 0 ] != '#':
                fields = line.split()
                lemma = fields[ 2 ]
                upostag = fields[ 3 ]
                if upostag == "VERB":
                    verb_dict[ lemma ] += 1
    return verb_dict
