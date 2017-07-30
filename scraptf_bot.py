import re
from the_bot import TheBot
from subprocess import Popen


QUEUE_HASH_INDEX = 5
USER_ID_INDEX = 6
GROUP_ID_INDEX = 7
RAFFLE_ID_INDEX = 19


class ScrapTF(TheBot):
    def __init__(self, bot_name):
        super().__init__(bot_name)
        self._site_url = 'https://scrap.tf/'
        self._queue_hash = None
        self._user_id = None
        self._group_id = None
        self._raffle_id = None

    def start(self):
        self.init_bot()
        self.get_user_info()

        while True:
            # Parse raffle page
            pass

    def get_page(self, url):
        # Reinvoke socket connection every time we get the page
        pass

    def get_user_info(self):
        page = self.get_page(self._site_url)
        self.invoke_socket_connection()

        scraptf_script = page.findAll('script', attrs={'type': 'text/javascript'})[-1]
        script_content = scraptf_script.get_text()

        raffle_string = script_content.splitlines()[RAFFLE_ID_INDEX]
        user_string = script_content.splitlines()[USER_ID_INDEX]
        queue_hash_string = script_content.splitlines()[QUEUE_HASH_INDEX]
        group_id_string = script_content.splitlines()[GROUP_ID_INDEX]

        raffle_id = re.search('"(.*?)"', raffle_string.strip())
        user_id = re.search('=(.*?);', user_string.strip())
        queue_hash_value = re.search('"(.*?)"', queue_hash_string.strip())
        group_id = re.search('=(.*?);', group_id_string.strip())

        self._raffle_id = raffle_id.group(0)
        self._user_id = user_id.group(1)
        self._queue_hash = queue_hash_value.group(0)
        self._group_id = group_id.group(1)

        self.invoke_socket_connection()


    def invoke_socket_connection(self):
        node_proc = Popen(['node', 'scraptf_bot.js', self._user_id, self._group_id, self._queue_hash, self._raffle_id])


