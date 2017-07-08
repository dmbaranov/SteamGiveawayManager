import re
import sys
import time
import requests
import configparser
from termcolor import colored
from datetime import datetime
from bs4 import BeautifulSoup


# Maps messages types to its colors
msg_type = {
    'SUCCESS':  'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'INFO':     'magenta'
}

# User agent for the requests
request_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


class TheBot:
    """
    Main class for the bots which contains default field and methods that every boot needs.
    """
    def __init__(self, bot_name):
        """
        Initializing bot with name, session and other empty values
        :param bot_name: bot's name. Should be equal to the section in the cookie.ini file
        """
        self._session = requests.Session()
        self._bot_name = bot_name
        self._user_name = ''
        self._points = -1
        self._site_url = ''
        self._cache = []
        self._cache_size = 150

    def init_bot(self):
        """
        Load cookies for the bot.
        """
        # optionsxform disable transformation of the cookies to uppercase
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('cookies.ini')

        try:
            bot_cookies = config[self._bot_name]
        except KeyError:
            self.print_message('No cookies for this bot', msg_type['ERROR'])
            sys.exit(1)

        for cookie_name in bot_cookies:
            self._session.cookies.set(cookie_name, bot_cookies[cookie_name])

        for k, v in request_headers.items():
            self._session.headers.update({k: v})
        # self._session.headers.update({'User-Agent': UA, 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': ACCEPT})
        self.print_message(f'Everything seems to be ready for {self._bot_name} bot', msg_type['SUCCESS'])

    def get_page(self, url):
        """
        Resolving page by given url, checks status code and returns its content
        :param url: resolves page by this url
        :return: bs4-ready content of the page
        """

        try:
            response = self._session.get(url)
        except requests.RequestException:
            self.print_message('Something went wrong with receiving a page', msg_type['ERROR'])
            return None

        if response.status_code != requests.codes.ok:
            self.print_message(f'Page has returned {response.status_code} code', msg_type['ERROR'])
            return None

        return BeautifulSoup(response.text, 'html.parser')

    def print_message(self, text, color='magenta'):
        """
        Prints message to the terminal with different colors
        :param text: message text
        :param color: message color
        """
        updated_text = f'[{datetime.now().strftime("%H:%M:%S")}] {self._bot_name}: {text}'
        message = colored(updated_text, color)
        print(message)

    @staticmethod
    def get_number(string):
        """
        Using regex extracts number from the given string
        :param string: string for parsing
        :return: number from the string
        """
        return int(re.search('[+-]?\d+(?:\.\d+)?', string).group(0))

    @staticmethod
    def pause_bot(sec):
        """
        Pauses a bot for given amount of seconds
        :param sec:
        """
        time.sleep(sec)
