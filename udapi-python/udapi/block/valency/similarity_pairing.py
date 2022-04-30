class Distance_measurer:
    def __init__( self, allow_substitution=True):
        self.edit_distance_minimum = self.levenshtein_minimum
        if not allow_substitution:
            self.edit_distance_minimum = self.lcs_minimum

    def compute_edit_distance( self, string_a, string_b):
        if string_a == "":
            return len( string_b)
        elif string_b == "":
            return len( string_a)
        elif string_a[0] == string_b[0]:
            return self.compute_edit_distance( string_a[1:], string_b[1:])
        else:
            return self.edit_distance_minimum( string_a[1:], string_b[1:])

    def lcs_minimum( self, string_a, string_b):
        insertion = self.compute_edit_distance( string_a[1:], string_b)
        deletion = self.compute_edit_distance( string_a, string_b[1:])
        return 1 + min( insertion, deletion)

    def levenshtein_minimum( self, string_a, string_b):
        ins_del_min_plus = self.lcs_minimum( string_a, string_b)
        substitution = self.compute_edit_distance( string_a[1:], string_b[1:])
        return min( ins_del_min_plus, 1 + substitution)

dm = Distance_measurer( allow_substitution=True)
string_a =