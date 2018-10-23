
class MenuParser:

    def __init__(self):
        pass

    def get_menu_string(self, timestamp):
        raise NotImplementedError()

    def closed_string(self):
        return "Mensa is closed today!"

    def emojify_menu(self, menu_string: str):
        lower_menu = menu_string.lower()
        if "burger" in lower_menu:
            menu_string += " :hamburger:"
        if "poulet" in lower_menu:
            menu_string += " :chicken:"
        if "schnitzel" in lower_menu:
            menu_string += " :cut_of_meat:"
        return menu_string

