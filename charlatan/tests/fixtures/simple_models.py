

class Toaster(object):

    def __init__(self, color, slots, content=None):
        self.color = color
        self.slots = slots
        self.content = content

    def __repr__(self):
        return "<Toaster '%s'>" % self.color


class User(object):

    def __init__(self, toasters):
        self.toasters = toasters
