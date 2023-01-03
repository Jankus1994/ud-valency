import sys

def combination_method( a_pairs, b_pairs):
    a_pairs_set = set( a_pairs)
    b_pairs_set = set( b_pairs)
    intersect_pairs_set = a_pairs_set & b_pairs_set
    intersect_pairs = list( intersect_pairs_set)
    a_only_pairs = list( a_pairs_set - intersect_pairs_set)
    b_only_pairs = list( b_pairs_set - intersect_pairs_set)
    return intersect_pairs, a_only_pairs, b_only_pairs

# def intersect_method( a_pairs, b_pairs):
#     intersect_pairs = list( set( a_pairs) & set( b_pairs))
#     return intersect_pairs
#
# def union_method( a_pairs, b_pairs):
#     union_pairs = list( set( a_pairs) | set( b_pairs))
#     return union_pairs

if __name__ == "__main__":
    a_align_file_name = sys.argv[ 1 ]
    b_align_file_name = sys.argv[ 2 ]
    output_file_name = sys.argv[ 3 ]

    with open( a_align_file_name, 'r') as a_align_file, \
            open( b_align_file_name, 'r') as b_align_file:
        a_num_lines = sum( 1 for line in a_align_file)
        b_num_lines = sum( 1 for line in b_align_file)

    if a_num_lines == b_num_lines:
        a_align_file = open( a_align_file_name, 'r')
        b_align_file = open( b_align_file_name, 'r')
        output_file = open( output_file_name, 'w')
        for i in range( a_num_lines):
            a_aligns = a_align_file.readline().split()
            b_aligns = b_align_file.readline().split()
            intersect_pairs, a_only_pairs, b_only_pairs = \
                    combination_method( a_aligns, b_aligns)
            intersect_str = ' '.join( [ pair.replace( '-', '=') for pair in intersect_pairs ])
            a_only_str = ' '.join( [ pair.replace( '-', '>') for pair in a_only_pairs ])
            b_only_str = ' '.join( [ pair.replace( '-', '<') for pair in b_only_pairs ])
            final_str = intersect_str + ' ' + a_only_str + ' ' + b_only_str + '\n'
            output_file.write( final_str)

        a_align_file.close()
        b_align_file.close()
        output_file.close()

