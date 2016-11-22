class Follower:
    def __init__(self, kind='knife', offset=0, radius=None):
        self.kind = kind
        self.offset = offset
        self.radius = radius

    def update(self, kind, offset, radius):
        if kind is not None:
            self.kind = kind
        if offset is not None:
            self.offset = offset
        if radius is not None:
            self.radius = radius
