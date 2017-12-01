import requests
from bs4 import BeautifulSoup

from menus.menu import Menu

class Inspira(Menu):

    def __init__(self):
        self.url = 'https://www.mediconvillage.se/sv/restaurant-cafe-inspira'
        self.menu = {}
        # swedish day of week names
        self.dow = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}
    
    def __repr__(self):
        return ":poop: Inspira"

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
        menu_list = soup.find('div', {'class': 'owl-carousel'})
        
        for li in menu_list.find_all('div', recursive=False):
            # get the day of week
            weekday = li.find('h3', {}).text.strip().lower()
            # get the dishes of the day
            day = li.find('div', {})
            day_strings = list(day.strings)

            # split by all tags essentially, we get something like
            # ['Fredag 11/7', 'Dagens Inspira:', 'a', 'Dagens 2:', 'b', ...]
            # so just skip the first one and then pair things.
            def pairwise(iterable):
                "s -> (s0, s1), (s2, s3), (s4, s5), ..."
                a = iter(iterable)
                return zip(a, a)
            dishes = ["".join([a, b]) for a, b in pairwise(day_strings[1:])]

            # add the list of dishes to the menu
            self.menu[weekday] = dishes
        
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
