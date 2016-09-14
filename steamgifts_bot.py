import re
from random import randint
from bs4 import BeautifulSoup
from the_bot import TheBot

class SteamgiftsBot(TheBot):
    """
    Bot for Steamgifts.com
    """
    def __init__(self, bot_name, cookies):
        """
        Initiating bot
        :param bot_name: name of the current bot
        :param cookies: section in settings.ini with cookies
        """
        super().__init__(bot_name, cookies)
        self._user_points = 0

    def start(self):
        """
        Starting current bot
        """
        self.start_bot()
        self.parse_page()

    def get_user_points(self):
        """
        Getting current amount of points
        """
        page = self.get_page("https://www.steamgifts.com/")
        points_parser = BeautifulSoup(page, "html.parser")
        try:
            self._user_points = int(points_parser.find_all(class_="nav__points")[0].text)
        except IndexError as err:
            self.print_message("Error while reading information about your points: {0}".format(err), "ERROR")

    def parse_page(self):
        """
        Parsing main page and looking for giveaways
        """
        page = self.get_page("https://www.steamgifts.com/")
        page_parser = BeautifulSoup(page, "html.parser")
        giveaways = page_parser.find_all(class_="giveaway__heading__name")

        for giveaway in giveaways:
            self.get_user_points()
            # Because there are too many giveaways per page, we pause this bot until it has at least 10 points
            if self._user_points > 10:
                self.parse_giveaway_page(giveaway)
            else:
                self.print_message("Sleeping for 1 hour... ", "WARNING")
                self.pause_bot(3600)
                self.parse_page()
        else:
            self.print_message("Sleeping for 1 hour... ", "WARNING")
            self.pause_bot(3600)
            self.parse_page()

    def parse_giveaway_page(self, ga_page):
        """
        Parsing giveaway page and entering it if possible
        :param ga_page: exact giveaway page
        """
        link = ga_page.get("href")
        giveaway_price = 0

        try:
            giveaway_price = int(re.findall(r'\d+', ga_page.next_sibling.text)[0])
        except IndexError:
            self.print_message("ERROR: Giveaway price wasn't found...", "ERROR")

        if self._user_points > giveaway_price:
            giveaway_page = self.get_page("https://steamgifts.com" + link)
            giveaway_parser = BeautifulSoup(giveaway_page, "html.parser")

            # For some reason not every giveaway has xsrf_token or code, that's why bot always checks it
            try:
                xsrf_token = giveaway_parser.find_all("input", {"name": "xsrf_token"})[0]["value"]
            except IndexError:
                self.print_message("ERROR: Giveaway token wasn't found, skipping this giveaway...", "ERROR")
                return

            try:
                code = giveaway_parser.find_all("input", {"name": "code"})[0]["value"]
            except IndexError:
                self.print_message("ERROR: Giveaway code wasn't found, skipping this giveaway...", "ERROR")
                return

            try:
                can_enter = giveaway_parser.find_all(class_="sidebar__entry-insert")[0]
            except IndexError:
                self.print_message("ERROR: Giveaway status wasn't found, skipping this giveaway...", "ERROR")
                return

            # If button for entering is equal to Enter Giveaway
            if "is-hidden" not in can_enter.get("class"):
                response = self._session.post("https://www.steamgifts.com/ajax.php",
                                              data={"xsrf_token": xsrf_token, "do": "entry_insert", "code": code})
                if response.status_code == 200:
                    self.print_message("Success!", "SUCCESS")
                else:
                    self.print_message("ERROR: Something went wrong: {0}".format(response.reason), "ERROR")
            else:
                self.print_message("You've entered this giveaway already", "WARNING")

            self.pause_bot(randint(3, 8))
        else:
            self.print_message("You don't have enough points to enter this giveaway", "WARNING")
