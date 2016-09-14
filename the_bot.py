import sys
import time
import configparser
import requests
from datetime import datetime

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2853.0 Safari/537.36"

TERMINAL_COLORS = {
    "SUCCESS": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m"
}


class TheBot():
    """Base class for all giveaways bots Contains a set of functions that all bots use."""

    def __init__(self, bot_name, cookies):
        """
        Object initialization.
        :param bot_name: name of the bot
        :param cookies: title of the section in settings.ini with the cookies for this bot
        """
        self._bot_name = bot_name
        self._cookies = cookies
        self._session = requests.Session()

    def start_bot(self):
        """
        Loading cookies and getting a page.
        """
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read("settings.ini")

        try:
            for item in config[self._cookies]:
                self._session.cookies.set(item, config[self._cookies][item])
        except KeyError as err:
            self.print_message("Error occured while reading cookies from the file: {0}".format(err), "ERROR")
            sys.exit(1)

        self._session.headers.update({"User-Agent": USER_AGENT})
        self.print_message("Settings has been loaded", "SUCCESS")

    def print_message(self, message="", color="WARNING"):
        """
        Prints different types of messages with different colors.
        :param message: message you want to print
        :param color: color of the message, use SUCCESS, WARNING or ERROR
        """
        cur_time = "[ {0} ] ".format(datetime.now().strftime("%H:%M:%S"))
        print(cur_time + "{0}: ".format(self._bot_name) + TERMINAL_COLORS[color] + str(message) + TERMINAL_COLORS["SUCCESS"])

    def get_page(self, url):
        """
        Makes a request to the page and returns it as html
        :param url: url of the web
        :return: returns page
        """

        r = self._session.get(url)
        if r.status_code == 200:
            return r.text
        else:
            self.print_message("Error occured while getting a page with the url: {0}".format(url), "ERROR")

    @staticmethod
    def pause_bot(sec):
        """
        When bot has finished with current page it sleeps and then starts again
        :param sec: how many second bot should sleep
        """
        time.sleep(sec)