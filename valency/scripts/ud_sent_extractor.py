import sys
with open( sys.argv[ 1 ], 'r') as conllu_file:
    for line in conllu_file:
        if "# text = " in line:
            sentence = line.rstrip( '\n').lstrip( "text = ")
            print( sentence)
