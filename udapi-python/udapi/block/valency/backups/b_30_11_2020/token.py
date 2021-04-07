from udapi.block.valency.role import Role

class Token:
    def __init__( self):
        self.form = ""
        self.role = Role.NONE
        self.space = True

    def set_form( self, form):
        self.form = form

    def set_role( self, role):
        self.role = role

    def set_space( self, space):
        self.space = space
