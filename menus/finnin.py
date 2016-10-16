
import requests
from bs4 import BeautifulSoup

from menus.menu import Menu

class FinnIn(Menu):

    def __init__(self):
        self.url = 'http://www.finninn.se/lunch-meny/'
        self.menu = {}
        # swedish day of week names
        self.dow = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}
    
    def __repr__(self):
        return "Finn In"

    def get_week(self):
        """
        Fetches the menu data from the given URL, returns a menu dictionary:
        {
            'dayofweek 1': ['dish 1', 'dish 2', ..., 'dish N'],
            'dayofweek 2': [ ... ]
        }
        """
        content = requests.get(self.url)
        soup = BeautifulSoup(content.text, 'html.parser')
        # menu list
        menu_list = soup.find('ul', {'class': 'menu-items'})
        for li in menu_list.find_all('li', recursive=False):
            # get the day of week
            weekday = li.find('div', {'class': 'grid2column'}).text.strip().lower()
            # get the dishes of the day
            dishes = li.find('div', {'class': 'item-description-menu'}).text

            # add the list of dishes to the menu
            self.menu[weekday] = dishes.strip().split('\n')
        
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
