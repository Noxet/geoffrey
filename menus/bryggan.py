
import requests
import collections

from bs4 import BeautifulSoup

from menus.menu import Menu

class Bryggan(Menu):

    def __init__(self):
        self.url = 'http://www.bryggancafe.se/veckans-lunch/'
        self.menu = collections.defaultdict(list)
        # swedish day of week names
        self.dow = {0: 'Måndag', 1: 'Tisdag', 2: 'Onsdag', 3: 'Torsdag', 4: 'Fredag'}
    
    def __repr__(self):
        return ":waterwave: Bryggan Kök och Café"

    def get_week(self):
        """
        Fetches the menu data from the given URL, returns a menu dictionary:
        {
            'dayofweek 1': ['dish 1', 'dish 2', ..., 'dish N'],
            'dayofweek 2': [ ... ]
        }
        """
        try:
            content = requests.get(self.url, timeout=3)
        except Exception:
            # return empty menu in case of timeouts etc.
            return dict()

        soup = BeautifulSoup(content.text, 'html.parser')
        # menu list
        menu_list = soup.find('div', {'class': 'et_pb_promo_description'})
        last_day = None
        for p in menu_list.find_all('p', recursive=False):
            # get data in each p-tag and ignore em and u tags.
            data = p.text.strip()
            if len(data) == 0:
                continue

            # remove trailing :
            if data[-1] == ':':
                data = data[:-1]

            # now determine if this is a day-label or menu.
            if data in self.dow.values():
                # it was a day label, note it down so we know when we see food
                last_day = data
                continue
            
            # if we reach here, it was probably food, anything that starts with
            # the string "Dagens:" or "Veg:" is considered food.
            if last_day and (data.startswith('Dagens:') or data.startswith('Veg:')):
                self.menu[last_day].append(data.strip())
        
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
