"""
This is a SteamGiveawaysBot Manager. It helps you to take part in different giveaways.
It's quite easy to insert a new bot, just inherit it from SuperGiveaway and create a parse function.
After that everything you need to do is to add it to the __init__ method of main class,
also don't forget to add it to the _bots array.

You may face a problem when some bots just won't do everything.
Because this is a multithreading manager, you should just increase amount of threads.
Best way is to have amount of threads that is equal to the amount of bots.

This is beta release.

PACKAGE = "---"
NAME = "Steambots Manager"
DESCRIPTION = "Probably the easiest way to enter the giveaways on different websites."
AUTHOR = "Dmitriy Baranov"
AUTHOR_EMAIL = "baranov.dmt@gmail.com"
URL = "https://github.com/theWaR13/SteamGiveawayManager"
VERSION = 0.4.0
"""

from multiprocessing.dummy import Pool as ThreadPool

from oppiumpulse_bot import OpiumpulsesBot
from steamgifts_bot import SteamgiftsBot
from gameminer_bot import GameminerBot
from indiegala_bot import IndiegalaBot


class SteamBotsManager:
    """
    Main class for controlling bots
    """

    def __init__(self):
        self._steamgifts_bot = SteamgiftsBot("Steamgifts", "STEAMGIFTS")
        self._opiumpulses_bot = OpiumpulsesBot("Opiumpulses", "OPIUMPULSES")
        self._gameminer_bot = GameminerBot("Gameminer", "GAMEMINER")
        self._indiegala_bot = IndiegalaBot("Indiegala", "INDIEGALA")
        self._bots = []

    def start(self):
        """
        Starts all bots in threads
        """
        self._bots.append(self._steamgifts_bot)
        self._bots.append(self._opiumpulses_bot)
        self._bots.append(self._gameminer_bot)
        self._bots.append(self._indiegala_bot)
        pool = ThreadPool(4)
        pool.map(self.start_bot, self._bots)
        pool.close()
        pool.join()

    @staticmethod
    def start_bot(bot):
        """
        Calls 'start' method in super class for bots to actually start them
        :param bot: current bot from the cycle which will be started
        """
        bot.start()


if __name__ == "__main__":
    sbm = SteamBotsManager()
    sbm.start()
