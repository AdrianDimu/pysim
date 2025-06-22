class Tile:
    def __init__(self, type_name):
        self.type = type_name
        self.building = None  # Later we'll store a machine here
        self.highlighted = False

    def is_buildable(self):
        return self.type in {"clear"}
