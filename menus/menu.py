
class Menu:
    """ Generic super class """

    def get_week(self):
        raise NotImplementedError
    
    def get_day(self, dow):
        raise NotImplementedError
