import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from the_bot import TheBot, msg_type

RAFFLES_LIST_URL = 'raffles/ending'
WAIT_TIME = 4
recaptcha_solver_url = 'http://2captcha.com/in.php' \
                       '?key={0}' \
                       '&method=userrecaptcha' \
                       '&googlekey={1}' \
                       '&pageurl={2}'

recaptcha_result_url = 'http://2captcha.com/res.php' \
                       '?key={0}' \
                       '&action=get' \
                       '&id={1}'


class ScrapTF(TheBot):
    def __init__(self, bot_name):
        super().__init__(bot_name)
        self._site_url = 'https://scrap.tf/'
        self._2captcha_api_key = None
        self._driver = None

    def init_bot(self):
        bot_cookies = super().init_bot()
        self._driver.get(self._site_url)

        with open('variables.env') as f:
            line = f.readline()
            line_content = line.split('=')
            if line_content[0] == '2captchaApiKey':
                self._2captcha_api_key = line_content[1]

        for cookie in bot_cookies:
            # We need special fields for this scr_session cookie
            if cookie == 'scr_session':
                self._driver.add_cookie({
                    'name': cookie,
                    'value': bot_cookies[cookie],
                    'secure': True,
                    'domain': '.scrap.tf'
                })
            else:
                self._driver.add_cookie({
                    'name': cookie,
                    'value': bot_cookies[cookie],
                    'path': '/'
                })

    def start(self):
        chrome_options = Options()
        chrome_options.add_argument('headless')
        chrome_options.add_argument('disable-gpu')

        self._driver = webdriver.Chrome(chrome_options=chrome_options)
        self.init_bot()

        if not self._2captcha_api_key:
            self.print_message('Provide 2captcha API key in format 2captchaApiKey=value in file variables.env',
                               msg_type['ERROR'])
            sys.exit(1)

        while self.get_user_info():
            self.get_raffles_page()
            self.print_message('Sleeping...', msg_type['INFO'])
            self.pause_bot(3600)

        self.print_message('Authentication failed, please check your cookies', msg_type['ERROR'])
        sys.exit(1)

    def get_user_info(self):
        self._driver.get('https://scrap.tf')
        self._driver.implicitly_wait(WAIT_TIME)

        user = self._driver.find_elements_by_class_name('nav-userinfo')

        return len(user) > 0

    def get_raffles_page(self):
        raffles_list = []
        self._driver.get(self._site_url + 'raffles/ending')

        bot_prevention = self._driver.find_elements_by_class_name('panel-bot-prevention')

        if len(bot_prevention) > 0:
            self.bypass_bot_prevention()
        else:
            for i in range(5):
                # Scrolling to the bottom to upload more raffles
                self._driver.execute_script('window.scrollTo(0, document.body.scrollHeight - 1000);')
                time.sleep(5)

            raffles = self._driver.find_elements_by_class_name('panel-raffle')
            for raffle in raffles:
                try:
                    not_joined = len(raffle.get_attribute('style')) == 0
                except WebDriverException:
                    self.print_message('Skipping...', msg_type['ERROR'])
                    continue

                if not_joined:
                    raffles_list.append(raffle.get_attribute('id')[-6:])

        for index, item in enumerate(raffles_list):
            self.print_message('Completing raffle {0} of {1}'.format(index, len(raffles_list)), msg_type['INFO'])
            self._driver.get(self._site_url + 'raffles/' + item)
            self.process_raffles(item)

    def process_raffles(self, raffle_id):
        try:
            button = self._driver.find_elements_by_id('raffle-enter')[0]
        except IndexError:
            self.print_message('Skipping', msg_type['ERROR'])
            return

        if 'btn-danger' in button.get_attribute('class'):
            return

        try:
            button.click()
        except WebDriverException:
            self.print_message('Skipping', msg_type['ERROR'])
            return

        time.sleep(WAIT_TIME)
        try:
            outer_elem = self._driver.find_elements_by_id('enter-button-outside')[0]
            recaptcha_elem = outer_elem.find_elements_by_tag_name('iframe')[0]
            recaptcha_key = self.get_recaptcha_key(recaptcha_elem)
        except IndexError:
            self.print_message('Skipping...', msg_type['ERROR'])
            return

        current_url = self._site_url + 'raffles/' + raffle_id
        recaptcha_result = self.solve_recaptcha(recaptcha_key, current_url)

        if recaptcha_result:
            try:
                button_enter = self._driver.find_elements_by_id('raffle-enter')[0]
            except IndexError:
                self.print_message('Skipping...', msg_type['ERROR'])
                return
            
            raffle_hash = button_enter.get_attribute('onclick').split("'")[3]

            self._driver.execute_script(
                "ScrapTF.Raffles.EnterRaffle('{0}', '{1}', '{2}')".format(raffle_id, raffle_hash, recaptcha_result))
            self.print_message('Successfully entered!', msg_type['SUCCESS'])
        else:
            self.print_message('Can\' solve a reCaptcha', msg_type['ERROR']) 

        self._driver.get(self._site_url + RAFFLES_LIST_URL)
        time.sleep(WAIT_TIME)

    def solve_recaptcha(self, recaptcha_key, current_url):
        recaptcha_request = self.get_page(recaptcha_solver_url.format(
            self._2captcha_api_key, recaptcha_key, current_url))

        recaptcha_request = str(recaptcha_request)

        if recaptcha_request[:2] == 'OK':
            retries = 0
            while retries <= 20:
                time.sleep(8)
                response = self.get_page(recaptcha_result_url.format(
                    self._2captcha_api_key, int(recaptcha_request[3:])))

                response = str(response)

                if response[:2] == 'OK':
                    # Can simplify while cycle, leave retries only
                    return response[3:]
                else:
                    retries += 1
        return None

    @staticmethod
    def get_recaptcha_key(recaptcha_elem):
        return recaptcha_elem.get_attribute('src').split('&')[0].split('=')[-1]

    def bypass_bot_prevention(self):
        try:
            recaptcha_elem = self._driver.find_elements_by_tag_name('iframe')[0]
        except IndexError:
            self.print_message('Can\'t bypass bot prevention')
            return

        recaptcha_key = self.get_recaptcha_key(recaptcha_elem)
        recaptcha_result = self.solve_recaptcha(recaptcha_key, self._site_url + RAFFLES_LIST_URL)

        if recaptcha_result:
            # Call js method for authentication
            pass
        else:
            self.print_message('Can\'t bypass bot prevention')
