import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
        self._websocket_proc = None

    def start(self):
        self.init_bot()

        chrome_options = Options()
        # chrome_options.add_argument('headless')
        # chrome_options.add_argument('disable-gpu')

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get('https://scrap.tf/raffles')

        driver.implicitly_wait(15)
        # self.invoke_socket_connection()
        me = driver.find_elements_by_class_name('nav-userinfo')
        print(me)

        # self.get_user_info()

        # while True:
        #     # Parse raffle page
        #     pass
        # self.get_raffles_page()

    def get_page(self, url):
        # Killing current websocket connection via killing the process
        if hasattr(self._websocket_proc, 'kill'):
            self._websocket_proc.kill()

        # Reinvoke socket connection every time we get the page
        if self._raffle_id and self._queue_hash and self._user_id and self._group_id:
            self.invoke_socket_connection()

        return super().get_page(url)

    def get_user_info(self):
        page = self.get_page(self._site_url)

        scraptf_script = page.find_all('script', attrs={'type': 'text/javascript'})[-1]
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
        self._websocket_proc = Popen(['node', 'scraptf_bot.js', self._user_id, self._group_id, self._queue_hash, self._raffle_id])

    def get_raffles_page(self):
        page = self.get_page(self._site_url + 'raffles')
        print(page.prettify())

        # if page.find('div', attrs={'class': 'panel-bot-prevention'}):
        #     print('Found initial bot prevention')
        #
        #     recaptcha_element = page.find_all('iframe', attrs={'src': re.compile('google')})
        #     print(recaptcha_element)


