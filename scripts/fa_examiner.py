import sys

def examine_side( pairs):
    a_items = []
    b_items = []
    for a_item, b_item in pairs:
        a_items.append( int( a_item))
        b_items.append( int( b_item))
    a_sorted = True
    if len( a_items) > 0:
        a_sorted = len( a_items) - 1 == sorted( a_items)[ - 1]
    b_sorted = True
    if len( b_items) > 0:
        b_sorted = len( b_items) - 1 == sorted( b_items)[ - 1]
    #print( a_items)
    #print( sorted(a_items))
    #print( b_items)
    #print( sorted( b_items))
    #print( "==")
    return a_sorted, b_sorted



def combination_method( a_pair_strs, b_pair_strs, i):
    a_pairs = [ pair_str.split( '-') for pair_str in a_pair_strs ]
    b_pairs = [ pair_str.split( '-') for pair_str in b_pair_strs ]
    aa, ab = examine_side( a_pairs)
    ba, bb = examine_side( b_pairs )
    if not( ab and ba ) and len( a_pair_strs) <= 6 and len( b_pair_strs) <= 6:
        print( i)

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
    #output_file_name = sys.argv[ 3 ]

    with open( a_align_file_name, 'r') as a_align_file, \
            open( b_align_file_name, 'r') as b_align_file:
        a_num_lines = sum( 1 for line in a_align_file)
        b_num_lines = sum( 1 for line in b_align_file)

    if a_num_lines == b_num_lines:
        a_align_file = open( a_align_file_name, 'r')
        b_align_file = open( b_align_file_name, 'r')
        #output_file = open( output_file_name, 'w')
        for i in range( a_num_lines):
            a_aligns = a_align_file.readline().split()
            b_aligns = b_align_file.readline().split()
            combination_method( a_aligns, b_aligns, i)
            #exit()


        a_align_file.close()
        b_align_file.close()
        #output_file.close()

