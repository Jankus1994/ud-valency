import sys

def examine( input_name):
    sent_num = 0
    zero_sent_num = 0
    triv_sent_num = 0
    nontriv_sent_num = 0
    all_pairs_num = 0
    triv_pairs_num = 0
    all_a_num = 0
    all_b_num = 0

    with open( input_name, 'r') as input_file:
        for line in input_file:
            sent_num += 1
            fields = line.split( '\t')

            pairs_str = fields[ 0 ]
            pairs_num = 0
            if pairs_str != "":
                pairs = pairs_str.split( ' ')
                pairs_num = len( pairs)
                all_pairs_num += pairs_num

            a_verbs_str = fields[ 1 ]
            a_num = 0
            if a_verbs_str != "":
                a_verbs = a_verbs_str.split( ' ')
                a_num = len( a_verbs)
                all_a_num += a_num

            b_verbs_str = fields[ 2 ]
            b_num = 0
            if b_verbs_str != "":
                b_verbs = b_verbs_str.split( ' ')
                b_num = len( b_verbs)
                all_b_num += b_num

            #print( i, a_num, b_num, file=sys.stderr)

            if a_num * b_num == 0:
                zero_sent_num += 1
            elif a_num * b_num == 1:
                triv_sent_num += 1
                if pairs_num == 1:
                    triv_pairs_num += 1
            elif a_num * b_num > 1:
                nontriv_sent_num += 1

    print( "====================")

    print( "all sent pairs", sent_num)
    print( "sent pairs with a*b=0", round( 100 * zero_sent_num / sent_num, 1))
    print( "sent pairs with a*b=1",  round( 100 * triv_sent_num / sent_num, 1))
    print( "of that gold", round( 100 * triv_pairs_num / sent_num, 1))
    print( "sent pairs with a*b>1", round( 100 * nontriv_sent_num / sent_num, 1))


    print( "a verbs", all_a_num)
    print( "b verbs", all_b_num)
    print( "gold verb pairs", all_pairs_num)
    print( "of that trivial", round( 100 * triv_pairs_num / all_pairs_num, 1))

    print( "====================")


if __name__ == "__main__":
    input_name = sys.argv[ 1 ]
    examine( input_name)



