class Max_matching_finder:
    def __init__( self):
        self.act_opt_init = 0

    def improving_comparison( self, new_val, act_opt_val):
        if new_val > act_opt_val:
            return True
        return False

    def compute_pairs_value( self, pairs_list, value_table):
        sum_value = 0
        for a_index, b_index in pairs_list:
            pair_value = value_table[ a_index ][ b_index ]
            sum_value += pair_value
        return sum_value

    def greedy_phase( self, a_num, b_num, a_matched, b_matched, value_table, pairs_list):
        sum_opt_val = self.compute_pairs_value( pairs_list, value_table)

        while True:
            found_improve = False
            opt_value = self.act_opt_init
            a_opt_index = None
            b_opt_index = None
            for a_index in range( a_num):
                if a_matched[ a_index ]:
                    continue
                for b_index in range( b_num):
                    if b_matched[ b_index ]:
                        continue

                    act_value = value_table[ a_index ][ b_index ]
                    if act_value is None:
                        continue
                    if self.improving_comparison( act_value, opt_value):
                        found_improve = True
                        opt_value = act_value
                        a_opt_index = a_index
                        b_opt_index = b_index
            if found_improve:
                sum_opt_val += opt_value
                a_matched[ a_opt_index ] = True
                b_matched[ b_opt_index ] = True
                chosen_pair = ( a_opt_index, b_opt_index )
                pairs_list.append( chosen_pair)
            else:
                break
        return pairs_list, sum_opt_val

    def tryall_phase( self, a_num, b_num, a_matched, b_matched,
                     value_table, pairs_list, depth_left):
        if depth_left == 0:
            greedy_pairs_list, greedy_val = self.greedy_phase( a_num, b_num,
                    a_matched, b_matched, value_table, pairs_list)
            return greedy_pairs_list, greedy_val

        if sum( a_matched) == a_num or sum( b_matched) == b_num:
            # all indices from the smaller side were already paired
            value = self.compute_pairs_value( pairs_list, value_table)
            return pairs_list, value

        opt_val = self.act_opt_init
        opt_pairs_list = []
        for a_index in range( a_num):
            if a_matched[ a_index ]:
                continue
            for b_index in range( b_num):
                if b_matched[ b_index ]:
                    continue
                if value_table[ a_index ][ b_index ] is None:
                    continue

                new_pair = ( a_index, b_index )
                new_pairs_list = pairs_list.copy() + [ new_pair ]
                a_matched[ a_index ] = True
                b_matched[ b_index ] = True
                branch_pairs_list, branch_val = self.tryall_phase(
                        a_num, b_num, a_matched, b_matched, value_table,
                        new_pairs_list, depth_left - 1)
                a_matched[ a_index ] = False
                b_matched[ b_index ] = False
                if self.improving_comparison( branch_val, opt_val):
                    opt_val = branch_val
                    opt_pairs_list = branch_pairs_list
        return opt_pairs_list, opt_val

    def find_matching( self, a_num, b_num, value_table):
        a_matched = [ False ] * a_num
        b_matched = [ False ] * b_num
        pairs_list = []
        allowed_depth = 3

        opt_pairs_list, opt_val = self.tryall_phase( a_num, b_num,
                a_matched, b_matched, value_table, pairs_list, allowed_depth)
        return opt_pairs_list, opt_val

class Min_matching_finder( Max_matching_finder):
    def __init__( self):
        self.act_opt_init = 1000

    def improving_comparison( self, new_val, act_opt_val):
        if new_val < act_opt_val:
            return True
        return False

if __name__ == "__main__":
    a_num = 4
    b_num = 6
    value_table = [
        [ 0.4, 1.6, 0.0, 0.9, 2.1, 2.2 ],
        [ 0.6, 2.6, 0.1, 2.3, 4.7, 1.6 ],
        [ 2.7, 0.7, 2.2, 2.8, 1.2, 1.5 ],
        [ 3.4, 5.2, 0.6, 1.9, 3.6, 2.6 ],
    ]
    chosen_pairs, sum_opt_val = greedy_MWB_matching(
        a_num, b_num, value_table, True)
    print( sum_opt_val)
    for a_index, b_index in chosen_pairs:
        value = value_table[ a_index ][ b_index ]
        print( a_index, b_index, value)
