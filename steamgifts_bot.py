import re
import sys
import json
import requests
from random import randint
from the_bot import TheBot, msg_type


class SteamgiftsBot(TheBot):
    def __init__(self, bot_name):
        super().__init__(bot_name)
        self._site_url = 'https://www.steamgifts.com'
        self._token = ''

    def start(self):
        self.init_bot()
        self.get_user_info()

        if self._points == -1 or not self._token or not self._user_name:
            self.print_message('Something went wrong while collecting data, exiting...')
            sys.exit(1)

        while True:
            self.parse_main_page()
            self.print_message('Sleeping for 1 hour...', msg_type['INFO'])
            self.pause_bot(3600)
            self.print_message('Awaking...', msg_type['INFO'])

            self.get_user_info()
            if len(self._cache) > self._cache_size:
                self._cache = []

    def get_user_info(self):
        page = self.get_page(self._site_url)
        if not page:
            return

        self._user_name = page.find('a', attrs={'class': 'nav__avatar-outer-wrap'})['href'][6:]
        self._points = int(page.find('span', attrs={'class': 'nav__points'}).string) or -1
        self._token = page.find('input', attrs={'type': 'hidden', 'name': 'xsrf_token'})['value']

    def parse_main_page(self):
        main_page = self.get_page(self._site_url)
        if not main_page:
            return

        giveaway_list = main_page.find_all('div', attrs={'data-game-id': re.compile(r'[+-]?\d+(?:\.\d+)?')})
        for giveaway in giveaway_list:
            if self._points == 0:
                self.print_message(f'You don\'t have points, sleeping for 1 hour... ', msg_type['WARNING'])
                return

            giveaway_code = giveaway.find('a', attrs={'class': 'giveaway__heading__name'})['href'].split('/')[2]
            giveaway_name = giveaway.find('a', attrs={'class': 'giveaway__heading__name'}).text
            giveaway_url = giveaway.find('a', attrs={'class': 'giveaway__heading__name'})['href']
            can_enter_giveaway = self.get_giveaway_status(giveaway_url, giveaway_name, giveaway_code)

            if not can_enter_giveaway:
                continue

            self.enter_giveaway(giveaway_code, giveaway_name)

    def get_giveaway_status(self, url, raw_name, code):
        """
        Receives giveaway page and checks if user can enter or not
        :param url: giveaway url
        :param name: name of the giveaway
        :param code: code of the giveaway
        :return: boolean, if can join giveaway or not
        """
        name = raw_name.encode('utf-8').decode('utf-8')
        self.pause_bot(randint(3, 8))
        if code in self._cache:
            self.print_message(f'You\'ve already entered {name}, skipping... ', msg_type['WARNING'])
            return False

        giveaway_page = self.get_page(f'{self._site_url}/{url}')
        if not giveaway_page:
            return False

        enter_buttons = giveaway_page.find_all('div', attrs={'data-do': 'entry_insert'})

        if not enter_buttons:
            self.print_message(f'Can\'t enter {name}, skipping... ', msg_type['WARNING'])
            return False
        for button in enter_buttons:
            if 'is-hidden' in button['class']:
                self.print_message(f'You\'ve already entered {name}, skipping... ', msg_type['WARNING'])
                return False
            else:
                giveaway_price = self.get_number(button.text)
                if giveaway_price > self._points:
                    self.print_message(f'You don\'t have enough points to enter {name}, skipping... ',
                                       msg_type['WARNING'])
                    return False
        return True

    def enter_giveaway(self, code, raw_name):
        name = raw_name.encode('utf-8').decode('utf-8')
        giveaway_url = self._site_url + '/ajax.php'
        giveaway_data = {
            'xsrf_token': self._token,
            'code': code,
            'do': 'entry_insert'
        }

        try:
            response = self._session.post(giveaway_url, data=giveaway_data)
        except requests.RequestException:
            self.print_message('Something went wrong with receiving a page', msg_type['ERROR'])

        if response.status_code == requests.codes.ok:
            response_text = json.loads(response.text)
            if response_text['type'] == 'success' and self._points != response_text['points']:
                self.print_message(f'Successfully entered {name}', msg_type['SUCCESS'])
                self._points = int(response_text['points'])
                self._cache.append(code)
            else:
                self.print_message(f'Error occured while entering {name}, skipping... ', msg_type['SUCCESS'])
