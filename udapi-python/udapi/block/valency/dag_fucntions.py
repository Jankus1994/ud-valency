"""
comp_function compares two items on their linear ordering
return one of the values -1, 0, 1:
I-item is preceding J-item ... 1
J-item is preceding I-item ... -1
items non linearly comparable ... 0
function must guarantee not to create cycles

table[ i ][ j ] ... relation of I-item to J-item
-1, 0, 1, similar as above
"""

def create_dag( items, comp_func):
    empty_table = [ [ 0 ] * len( items) for i in range( len( items)) ]
    allrels_table = set_all_rels( items, comp_func, empty_table)
    dag_table = delete_redundants( allrels_table)
    return dag_table

def set_all_rels( items, comp_func, rels_table):
    for i , i_item in enumerate( items):
        for j, j_item in enumerate( items):
            if j > i:
                comp_result = comp_func( i_item, j_item)
                rels_table[ i ][ j ] = comp_result
                rels_table[ j ][ i ] = - comp_result
    return rels_table

def delete_redundants( rels_table):
    for pivot_index in range( len( rels_table)):
        queue = []
        for other_index in range( len( rels_table)):
            if rels_table[ pivot_index ][ other_index ] == 1:
                queue.append( other_index)
        while queue != []:
            a_index = queue.pop( 0)
            a_row = rels_table[ a_index ]
            for b_index, ab_rel in enumerate( a_row):
                if ab_rel == 1:
                    queue.append( b_index)
                    rels_table[ pivot_index ][ b_index ] = 0
                    rels_table[ b_index ][ pivot_index ] = 0
    return rels_table

# table = [
#     [ 0, 0, 1, 1, 0, 1, 0, 1, 1],
#     [ 0, 0, 0, 1, 1, 0, 1, 1, 1],
#     [-1, 0, 0, 0, 0, 1, 0, 0, 0],
#     [-1,-1, 0, 0, 0, 0, 0, 1, 1],
#     [ 0,-1, 0, 0, 0, 0, 1, 1, 1],
#     [-1, 0,-1, 0, 0, 0, 0, 0, 0],
#     [ 0,-1, 0, 0,-1, 0, 0, 1, 1],
#     [-1,-1, 0,-1,-1, 0,-1, 0, 1],
#     [-1,-1, 0,-1,-1, 0,-1,-1, 0]
# ]
# def test_comp_func( i, j):
#     return table[ i ][ j ]
#
# def test():
#     final_table = create_dag( list( range(9)), test_comp_func)
#     for row in final_table:
#         print( row)
# test()
