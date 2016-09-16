# SteamGiveawayManager
This is a Bot Manager that helps you to control all of your bots which enter giveaways instead of you. You can easily add more bots if you whish. In order to start using this manager you should:

1. Visit every giveaway website, get it cookies and add it to settings.ini. E.g. for steamgifts you should add PHPSESSID and _ga, order doesn't matter.
2. Install required modules: ``pip3 install requests bs4``
3. In folder with .py files open terminal and type : ``python main.py`` These scripts were tested on Linux with python3.5
4. If everything is ok, bots will load settings and start enter giveaways, otherwise you can open an issue and report a bug there.

Currently supported services:
* Steamgifts
* Indiegala (You may have some problems with it)
* Oppiumpulse
* Gameminer
