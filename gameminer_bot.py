from random import randint
from bs4 import BeautifulSoup
from the_bot import TheBot


class GameminerBot(TheBot):
    """
    Bot for Opiumpulses.com
    """
    def __init__(self, bot_name, cookies):
        """
        Initiating bot
        :param bot_name: name of the current bot
        :param cookies: section with cookies in settings.ini
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
        page = self.get_page("http://gameminer.net/")
        points_parser = BeautifulSoup(page, "html.parser")
        points = points_parser.find_all(class_="user__coal")
        self._user_points = int(points[0].text)

    def parse_page(self):
        """
        Parsing page and entering every available giveaway
        """
        page = self.get_page("http://gameminer.net/")
        page_parser = BeautifulSoup(page, "html.parser")
        giveaways = page_parser.find_all(class_="giveaway__container")

        for item in giveaways:
            self.get_user_points()
            giveaway_url = ""
            giveaway_price = ""

            try:
                giveaway_url = item.find_all(class_="giveaway-join")[0]["action"]
            except IndexError:
                self.print_message("You have already joined this giveaway or an error has occured, skipping", "WARNING")
                continue
            try:
                giveaway_price = int(item.find_all(class_="g-coal-icon g-white")[0].text[:-5])
            except IndexError:
                self.print_message("Something wrong with a giveaway, probably this one requires gold", "WARNING")
                continue

            if self._user_points < 5:
                self.print_message("Sleeping for 1 hour...", "WARNING")
                self.pause_bot(3600)
                self.parse_page()

            if self._user_points > giveaway_price:
                # Gameminer requires _xsrf cookie to be sent as Form data
                r = self._session.post("http://gameminer.net" + giveaway_url, data={"_xsrf": self._session.cookies.get("_xsrf"), "json": "true"})
                if r.status_code == 200:
                    self.print_message("Success", "SUCCESS")
                else:
                    self.print_message("Error: " + r.reason, "ERROR")
                self.pause_bot(randint(3, 8))
            else:
                self.print_message("You don't have enough points to enter this giveaway...", "WARNING")
                continue
        else:
            self.print_message("Sleeping for 1 hour...", "WARNING")
            self.pause_bot(3600)
            self.parse_page()