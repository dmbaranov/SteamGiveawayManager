import re
from random import randint
from bs4 import BeautifulSoup
from the_bot import TheBot


class OpiumpulsesBot(TheBot):
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
        page = self.get_page("http://www.opiumpulses.com/")
        points_parser = BeautifulSoup(page, "html.parser")
        points_str = points_parser.find_all("a", attrs={"style": "padding: 3px 10px;cursor: default;"})[0].text
        self._user_points = int(points_str[8:])

    def parse_page(self):
        """
        Parsing page and entering every available giveaway
        """
        page = self.get_page("http://www.opiumpulses.com/")
        page_parser = BeautifulSoup(page, "html.parser")
        giveaways = page_parser.find_all(class_="col-xs-4 col-md-3 well product-box")

        for giveaway in giveaways:
            self.get_user_points()
            giveaway_data = giveaway.find_all("a")
            # There should be 3 links if you haven't entered this giveaway yet
            if len(giveaway_data) <= 2:
                self.print_message("You have already entered this giveaway", "WARNING")
                continue

            giveaway_price = re.findall(r'\d+', giveaway_data[2].text)
            giveaway_url = giveaway_data[2]["href"]

            if len(giveaway_price) == 0 or self._user_points > int(giveaway_price[0]):
                r = self._session.get("http://www.opiumpulses.com" + giveaway_url)
                if r.status_code == 200:
                    self.print_message("Success!", "SUCCESS")
                    self.pause_bot(randint(3, 8))
                else:
                    self.print_message("Error has occured while entering giveaway: {0}".format(r.reason), "ERROR")
            elif self._user_points < giveaway_price:
                self.print_message("You don't have enough points to enter this giveaway", "WARNING")
                continue
            else:
                self.print_message("Sleeping for 1 hour...", "WARNING")
                self.pause_bot(3600)
                self.parse_page()
        else:
            self.print_message("Sleeping for 1 hour...", "WARNING")
            self.pause_bot(3600)
            self.parse_page()
