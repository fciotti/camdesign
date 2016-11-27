class Follower:
    def __init__(self, kind='roller', offset=0, radius=0):
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
