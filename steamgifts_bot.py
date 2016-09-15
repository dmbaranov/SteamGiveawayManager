import sys
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
        Starting a bot
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
            sys.exit(1)

    def parse_page(self):
        """
        Parsing main page and looking for giveaways
        """
        page = self.get_page("https://www.steamgifts.com/")
        page_parser = BeautifulSoup(page, "html.parser")
        giveaways = page_parser.find_all(class_="giveaway__row-outer-wrap")

        for giveaway in giveaways:
            self.pause_bot(randint(3, 8))
            self.get_user_points()
            giveaway_url = giveaway.find(class_="giveaway__heading__name")["href"]
            check_giveaway = self.has_already_entered(giveaway_url)

            if self._user_points < 10:
                self.print_message("Sleeping for 1 hour... ", "WARNING")
                self.pause_bot(3600)
                self.parse_page()

            if type(check_giveaway) == bool:
                self.print_message("You have already entered this giveaway, skipping...", "WARNING")
                continue

            else:
                if self._user_points > check_giveaway["price"]:
                    r = self._session.post("https://www.steamgifts.com/ajax.php",
                                                  data={"xsrf_token": check_giveaway["xsrf_token"], "do": "entry_insert", "code": check_giveaway["code"]})
                    if r.status_code == 200:
                        self.print_message("Success!", "SUCCESS")
                    else:
                        self.print_message("ERROR: Something went wrong: {0}".format(r.reason), "ERROR")

        else:
            self.print_message("Sleeping for 1 hour... ", "WARNING")
            self.pause_bot(3600)
            self.parse_page()

    def has_already_entered(self, url):
        giveaway_page = self.get_page("https://steamgifts.com" + url)
        giveaway_page_parser = BeautifulSoup(giveaway_page, "html.parser")

        try:
            enter_button = giveaway_page_parser.find_all(class_="sidebar__entry-insert")[0]["class"]
        except IndexError:
            self.print_message("You have already entered this giveaway, skipping...", "WARNING")
            return False

        if "is-hidden" in enter_button:
            return False
        else:
            giveaway_page_data = giveaway_page_parser.find_all(class_="sidebar sidebar--wide")[0]
            xsrf_token = giveaway_page_data.find("input", {"name": "xsrf_token"})["value"]
            code = giveaway_page_data.find("input", {"name": "code"})["value"]
            price = self.get_number(giveaway_page_parser.find_all(class_="featured__heading__small")[-1].text)

            return {
                "xsrf_token": xsrf_token,
                "code": code,
                "price": price
            }
