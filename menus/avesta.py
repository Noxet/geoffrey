
from menus.menu import Menu

class Avesta(Menu):

    def __init__(self):
        self.url = ''
        self.menu = {}
        # swedish day of week names
        self.dow = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}
    
    def __repr__(self):
        return ":pizza: Avesta Pizzeria"

    def get_week(self):
        """ Only eat pizza on fridays """
        self.menu['fredag'] = ['Lunds bästa pizza']
        return self.menu

    def get_day(self, dow):
        """
        Returns the menu, as a list, of the given day, dow,
        where 0 is Monday and 6 is Sunday.
        """
        # If the menu hasn't been fetched, do it, it will be cached.
        if self.menu == {}:
            self.get_week()
        
        dow_name = self.dow[dow]
        if dow_name not in self.menu:
            return ['404 - Food not found']
        return self.menu[dow_name]
