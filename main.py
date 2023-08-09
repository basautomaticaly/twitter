
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time,json,os
from bs4 import BeautifulSoup
from random import choice
from loguru import logger

if not os.path.exists('results.txt'):
    with open('results.txt','w',encoding='utf-8') as file:
        file.write('')

class Browser():
    def __init__(self):
        self.links_profile = []
        options = uc.ChromeOptions()
        options.add_argument('--headless') 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        self.driver = uc.Chrome(options=options,service=ChromeService(ChromeDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 40)
        os.system('cls' if os.name == 'nt' else 'clear')
        if not os.path.exists('cookies.json'):
            logger.info('[+] Куки не найдены, авторизуемся с логина и пароля')
            self.driver.get('https://twitter.com/i/flow/login')
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]')))
            self.authorize()
        else:
            logger.info('[+] Найдены куки, авторизуемся')
            self.driver.get('https://twitter.com/')
            with open('cookies.json','r',encoding='utf-8') as file:
                self.cookies = json.loads(file.read())
            self.authorize_by_cookie()
    def go_parse(self):
        
        logger.info('[+] Введите запрос (Пример: btc): ')
        self.parse_arg = input()
        self.url_parse = f'https://twitter.com/search?q={self.parse_arg}&src=typed_query&f=user'
        self.driver.get(self.url_parse)
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
        main_html = BeautifulSoup(self.driver.page_source,'lxml')
        all_links = main_html.find_all('a',{'role':'link'})
        for a in all_links:
            try:
                if a['href'][0] == '/' and len(a['href'].split('/')) == 2 and '?' not in a['href'] and a['href'] != '/home' and a['href'] != '/explore' and a['href'] != '/notifications' and a['href'] != '/messages':
                    if 'https://twitter.com'+a['href'] not in self.links_profile:
                        self.links_profile.append('https://twitter.com'+a['href'])
                        logger.info('Найден профиль: '+'https://twitter.com'+a['href'])
            except:
                pass
        while True:
            link = choice(self.links_profile)+'/following'
            self.driver.get(link)
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="cellInnerDiv"]')))
            main_html = BeautifulSoup(self.driver.page_source,'lxml')
            all_profiles = main_html.find_all('div',{'role':'button'})
            for profile in all_profiles:
                if 'r-1cvl2hr r-4qtqp9 r-yyyyoo r-1xvli5t r-9cviqr r-f9ja8p r-og9te1 r-bnwqim r-1plcrui r-lrvibr' in str(profile):
                    profile_link = (profile.find('a',{'role':'link'}))['href']
                    if 'https://twitter.com'+profile_link not in self.links_profile:
                        self.driver.get(f'https://twitter.com{profile_link}')
                        self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]')))
                        time.sleep(1)
                        if 'M1.998 5.5c0-1.381 1.119-2.5 2.5-2.5h15c1.381 0 2.5 1.119 2.5 2.5v13c0 1.381-1.119 2.5-2.5 2.5h-15c-1.381 0-2.5-1.119-2.5-2.5v-13zm2.5-.5c-.276 0-.5.224-.5.5v2.764l8 3.638 8-3.636V5.5c0-.276-.224-.5-.5-.5h-15zm15.5 5.463l-8 3.636-8-3.638V18.5c0 .276.224.5.5.5h15c.276 0 .5-.224.5-.5v-8.037z' in self.driver.page_source:
                            with open('results.txt','r',encoding='utf-8') as file:
                                info = file.read()
                            if f'https://twitter.com{profile_link}' not in info:
                                with open('results.txt','a',encoding='utf-8') as file:
                                    file.write(f'https://twitter.com{profile_link}\n')
                                logger.success(f'Найдена галочка! https://twitter.com{profile_link}')
                            else:
                                logger.error(f'Антипаблик - https://twitter.com{profile_link}')
                        else:
                            logger.warning(f'Найдена галочка! https://twitter.com{profile_link} (закрытая личка)')
                        self.links_profile.append('https://twitter.com'+profile_link)
            time.sleep(2)
    def authorize_by_cookie(self):
        for cookie in self.cookies:
            self.driver.add_cookie(cookie)
        self.driver.get('https://twitter.com/')
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//a[@href="/home"]')))
        main_html = BeautifulSoup(self.driver.page_source,'lxml')
        profile = main_html.find('a',{'data-testid':'AppTabBar_Profile_Link'})
        logger.success(f'Успешная авторизация - https://twitter.com{profile["href"]}')
        self.go_parse()
    def authorize(self):
        logger.info('[+] Введите почту: ')
        email = input()
        self.driver.find_element('xpath', '//input[@autocomplete="username"]').send_keys(f"{email}\n")
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password"]')))
        except:
            try:
                self.driver.find_element('xpath', '//input[@autocomplete="on"]')
                while True:
                    logger.error('[+] Подозрительный вход! Введите номер телефона от аккаунта или юзернэйм:')
                    phone = input()
                    self.driver.find_element('xpath', '//input[@autocomplete="on"]').send_keys(phone+'\n')
                    time.sleep(5)
                    try:
                        self.driver.find_element('xpath', '//input[@autocomplete="current-password"]')
                        time.sleep(3)
                        break
                    except:
                        logger.error('Неверный телефон или юзернэйм от аккаунта')
            except:
                logger.error('Не обработанная ошибка! Напишите продавцу!')
                quit()
        while True:
            logger.info('[+] Введите пароль: ')
            password = input()
            self.driver.find_element('xpath', '//input[@autocomplete="current-password"]').send_keys(f"{password}\n")
            time.sleep(5)
            try:
                self.driver.find_element('xpath', '//input[@autocomplete="current-password"]')
                logger.error('Введён неверный пароль!')
            except:
                break
        logger.success('Пароль верный!')
        if self.driver.current_url != 'https://twitter.com/home':
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="on"]')))
            while True:
                logger.info('[+] Введите код подтверждения:');code = input()
                self.driver.find_element('xpath', '//input[@autocomplete="on"]').send_keys(code+'\n')
                time.sleep(5)
                if self.driver.current_url == 'https://twitter.com/home':
                    break
                else:
                    logger.error('Введён неверный код подтверждения!')
        main_html = BeautifulSoup(self.driver.page_source,'lxml')
        profile = main_html.find('a',{'data-testid':'AppTabBar_Profile_Link'})
        logger.success(f'Успешная авторизация - https://twitter.com{profile["href"]}')
        with open('cookies.json','w',encoding='utf-8') as file:
            file.write(json.dumps(self.driver.get_cookies()))
        self.go_parse()
Browser()