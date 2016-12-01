class Follower:
    def __init__(self, flat=False, offset=0, radius=0):
        self.flat = flat
        self.offset = offset
        self.radius = radius

    def __getattr__(self, name):
        if name == 'kind':
            if self.flat:
                return 'flat'
            elif self.radius == 0:
                return 'knife'
            else:
                return 'roller'
        return None

    def update(self, flat, offset, radius):
        if flat is not None:
            self.flat = flat
        if offset is not None:
            self.offset = offset
        if radius is not None:
            self.radius = radius
