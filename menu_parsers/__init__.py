
class MenuParser:

    def __init__(self):
        pass

    def get_menu_string(self, timestamp):
        raise NotImplementedError()

    def closed_string(self):
        return "Mensa is closed today!"
