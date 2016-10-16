
import requests
import datetime

from menus.menu import Menu

class FinnUt(Menu):

    def __init__(self):
        self.url = 'http://finnut.se/ajax/menu.json.php'
        self.menu = {}
        # swedish day of week names
        self.dow = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}
    
    def __repr__(self):
        return "Finn Ut"

    def get_week(self):
        """
        Fetches the menu data from the given URL, returns a menu dictionary:
        {
            'dayofweek 1': ['dish 1', 'dish 2', ..., 'dish N'],
            'dayofweek 2': [ ... ]
        }
        """
        content = requests.get(self.url)
        menu_list = content.json()
        for menu in menu_list:
            # date is in the form yyyy-mm-dd
            date = menu['date'].split('-')
            weekday = datetime.date(int(date[0]), int(date[1]), int(date[2])).weekday()
            # skip weekends
            if weekday > 4: continue
            
            dow = self.dow[weekday]
            dishes = menu['content'].split('\n\n')
            # remove the newline for gluten-free etc. and put is between parantheses
            # yes, this is ugly a.f. TODO: make it pretty
            dishes = ['%s (%s)' % (i.split('\n')[0], i.split('\n')[1]) if len(i.split('\n')) > 1 else i.split('\n')[0] for i in dishes]
            self.menu[dow] = dishes

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
        return self.menu[dow_name]
