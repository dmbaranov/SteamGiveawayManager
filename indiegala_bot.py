# giv_id: "140214" - request payload
# ticket_price: "1"
#

from random import randint
from bs4 import BeautifulSoup
from the_bot import TheBot


class IndiegalaBot(TheBot):
    """
    Bot for Indiegala.com
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
        page = self.get_page("https://www.indiegala.com/giveaways")
        points_parser = BeautifulSoup(page, "html.parser")
        points = self.get_number(points_parser.find_all(class_="right coins-amount")[0]["title"])
        self._user_points = points

    def has_already_entered(self, url):
        page = self.get_page(url)
        page_parser = BeautifulSoup(page, "html.parser")

        giveaway_has_ticket = page_parser.find_all(class_="giv-coupon relative animated-coupon")

        if len(giveaway_has_ticket) == 0:
            return True
        else:
            return False

    def parse_page(self):
        """
        Parsing page and entering every available giveaway
        """
        page = self.get_page("https://www.indiegala.com/giveaways")
        page_parser = BeautifulSoup(page, "html.parser")
        giveaways = page_parser.find_all(class_="tickets-col")

        for item in giveaways:
            self.get_user_points()

            try:
                giveaway_url = item.find("a")["href"]
            except IndexError:
                self.print_message("You have already joined this giveaway or an error has occured, skipping", "WARNING")
                continue
            try:
                giveaway_price = self.get_number(item.find(class_="ticket-price").find("strong").text)
            except IndexError:
                self.print_message("Something wrong with a giveaway, probably this one requires gold", "WARNING")
                continue

            if self.has_already_entered("https://www.indiegala.com" + giveaway_url):
                self.print_message("You have already entered this giveaway, skipping...", "WARNING")
                continue

            if self._user_points > giveaway_price:
                giveaway_id = giveaway_url.split('/')[-1]
                r = self._session.post("https://www.indiegala.com/giveaways/new_entry",
                                       json={"giv_id": giveaway_id, "ticket_price": giveaway_price})
                if r.status_code == 200:
                    self.print_message("Success", "SUCCESS")
                    self.pause_bot(randint(3, 8))
                else:
                    self.print_message("Error: " + r.reason, "ERROR")
            else:
                self.print_message("You don't have enough points to enter this giveaway...", "WARNING")

        else:
            self.print_message("Sleeping for 1 hour...", "WARNING")
            self.pause_bot(3600)
            self.parse_page()
