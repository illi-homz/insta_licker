from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import os
from exeptions import NoLogin, BadURL

import db_objects as db

from random import randint


class SeeStorris:
    def __init__(self, login, password, user_url):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.user_login = login
        self.user_password = password
        self.client_url = user_url
        self.folowers_url_list = []
        self.how_much_need_to_see = 250 # сколько нужно посмотреть за сессию
        self.complete_folowers_list = []
        self.added_to_base = 0
        self.need_count_folowers = 0
        self.find_stories = False
        self.find_photos = False
        self.browser = webdriver.Chrome(
            self.BASE_DIR + '/browser_drivers/chromedriver'
        )

        # db work
        self.session = db.connect_db(db.DB_PATH)
        self.user = self.session.query(db.User).filter(db.User.name == login).first()
        if not self.user:
            self.user = db.User(name=login)
            self.session.add(self.user)
            self.session.commit()

    def run(self):
        if not self.login():
            print('ошибка входа')
            raise NoLogin('incorrect login or password')
        time.sleep(5)
        while True:
            self.folowers_url_list = self.no_complet_controll()
            # self.folowers_url_list = []
            if not self.folowers_url_list:
                self.browser.get(self.client_url)
                time.sleep(3)
                # self.need_count_folowers = self.get_count_folowers() # для всех подписчиков
                self.need_count_folowers = 500
                print(f'Подписчиков на странице - {self.need_count_folowers}')
                self.open_list_folowers()
                time.sleep(2)
                self.element = self.get_element() # окно списка подпписчиков
                self.scroll_list_and_get_folowers_urls()
                # break
                time.sleep(2)
                self.start_see_storris()
                break
            time.sleep(2)
            self.start_see_storris()
            print(f'{len(self.folowers_url_list)} посмотрел')
            # break
        self.browser.close()

    def login(self):
        # Вход в аккаунт
        self.browser.get('https://instagram.com/accounts/login')
        time.sleep(4)
        self.browser.find_element_by_xpath(
            '//section/main/div/article/div/div[1]/div/form/div[2]/div/label/input'
        ).send_keys(self.user_login)
        self.browser.find_element_by_xpath(
            '//section/main/div/article/div/div[1]/div/form/div[3]/div/label/input'
        ).send_keys(self.user_password)
        self.browser.find_element_by_xpath(
            '//section/main/div/article/div/div[1]/div/form/div[4]/button'
        ).click()

        time.sleep(2)

        try:
            self.browser.find_element_by_class_name('eiCW-')
            return False
        except NoSuchElementException:
            return True
    
    def no_complet_controll(self):
        no_complete_urls = self.session.query(
                db.CompleteFolower
            ).filter(
                db.CompleteFolower.viewed == 0,
                db.CompleteFolower.user_id == self.user.id,
            ).all()[:self.how_much_need_to_see]

        if no_complete_urls:
            return [url.url for url in no_complete_urls]
        else:
            return []

    def get_count_folowers(self):
        link_on_folowers = self.browser.find_element_by_xpath(
        '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span'
        )
        return int(link_on_folowers.get_attribute('title').replace(' ', '')) - 1

    def open_list_folowers(self):
        # Открываю окно с подписчиками
        self.link_on_folowers = self.browser.find_element_by_xpath(
            '//section/main/div/header/section/ul/li[2]/a'
        ).click()
    
    def get_element(self):
        # return self.browser.find_element_by_xpath('/html/body/div[4]/div/div[2]')
        return self.browser.find_element_by_class_name('isgrP')
    
    def scroll(self, heigth=1):
        self.browser.execute_script(f'arguments[0].scrollTop = arguments[0].scrollHeight/{heigth}', self.element)

    def get_folowers_urls(self):
        try:
            folowers = self.browser.find_elements_by_class_name('FPmhX')
            folowers = folowers[-250:len(folowers)]
            url_list = []
            for folower in folowers:
                f_url = str(folower.get_attribute('href'))

                if f_url in self.folowers_url_list:
                    continue

                # complete control
                complete_url = self.session.query(
                        db.CompleteFolower
                    ).filter(
                        db.CompleteFolower.url == f_url,
                        self.user.name == self.user_login
                    ).first()

                if complete_url:
                    if complete_url.viewed:
                        if f_url not in self.complete_folowers_list:
                            self.complete_folowers_list.append(f_url)
                        continue
                    url_list.append(f_url)
                    continue

                if f_url not in url_list:
                    url_list.append(f_url)

                    folower_url = db.create_folower_url(self.user, f_url)
                    self.session.add(folower_url)
                    self.session.commit()

                    self.added_to_base += 1

                    # print(f'В базу добавил {f_url} как не обработанного')

            # self.complete_folowers_list = len(folowers) - len(self.folowers_url_list) - len(url_list)
            return url_list
        except:
            print('Не могу найти пользователей')
            return []

    def scroll_list_and_get_folowers_urls(self):
        heigth_list = [6, 4, 3, 2]
        num_scroll = 0
        # sleep_time_befor_scroll = 4

        map(self.scroll, heigth_list)

        # all_complete = len(self.folowers_url_list) + self.complete_folowers_list
        
        while len(self.folowers_url_list) + len(self.complete_folowers_list) < self.need_count_folowers:

            num_scroll += 1
            self.scroll()

            if num_scroll % 10 == 0:
                self.folowers_url_list += self.get_folowers_urls()
                print('Всего: {0} Получил для обработки: {1} Добавлено в базу: {2} В пропуске: {3} Всего: {4}'.format(
                    self.need_count_folowers,
                    len(self.folowers_url_list),
                    self.added_to_base,
                    len(self.complete_folowers_list),
                    len(self.folowers_url_list) + len(self.complete_folowers_list)
                ))
                # print(self.need_count_folowers, len(self.folowers_url_list))

            time.sleep(randint(5, 20))

            # if len(self.folowers_url_list) > self.how_much_need_to_see:
            #     break

    def see_storis(self):
        # Просмотр сторисов
        start_time = time.monotonic()
        work_time = 29 # время просмотра сторисов
        try:
            list_storis = self.browser.find_elements_by_class_name('NCYx-')
            self.find_stories = True
            list_storis[0].click()
            time.sleep(3)
            while True:
                try:
                    self.browser.find_element_by_class_name('yS4wN')
                    if time.monotonic() - start_time > work_time:
                        close = self.browser.find_element_by_class_name('Szr5J')
                        close.click()
                    time.sleep(5)
                except:
                    break
            return
        except:
            self.find_stories = False
            return

    def start_see_storris(self):
        print('Пошла жара')
        max_f = 0

        start_time = time.monotonic()
        work_time = 0
        sleep_time = 0

        self.liked_folowers = 0
        max_like_in_hour = randint(55, 59)

        for url in self.folowers_url_list:
            # закончить при просмотре необходимого числа аккаунтов
            if self.liked_folowers == self.how_much_need_to_see:
                break

            # add url in complete_url from db
            folower_url = self.session.query(
                        db.CompleteFolower
                    ).filter(
                        db.CompleteFolower.url == url,
                        self.user.name == self.user_login
                    ).first()
            folower_url.viewed = 1
            self.session.add(folower_url)
            self.session.commit()
            print(f'{max_f}. {url}: пометил как обработанный')

            self.browser.get(url)
            time.sleep(3)

            self.see_storis()
            time.sleep(1)

            self.like_end_photo()

            if self.liked_folowers == max_like_in_hour: # Сон при лайканьи 60 подпизчиков
                work_time = time.monotonic() - start_time
                print(f'Время работы: {int(work_time/60)} минут')
                sleep_time = 3600 - work_time
                if sleep_time > 0:
                    print(f'Уснул на {int(sleep_time/60)} минут')
                    time.sleep(sleep_time)
                    print(f'Погнали дальше! Осталось {self.how_much_need_to_see - max_f}')
                max_like_in_hour = randint(52, 57)
                start_time = time.monotonic()
                self.liked_folowers = 0
            else:
                if self.find_photos or self.find_stories:
                    wait_time = randint(10, 40)
                    print(f'Ожидание {wait_time} с, отлайкано {self.liked_folowers}')
                    time.sleep(wait_time)
                else:
                    print('Ожидание 0 с')

            max_f += 1
    
    def like_end_photo(self):
        try:
            photos_on_page = self.browser.find_elements_by_class_name('eLAPa')
            self.find_photos = True
            end_photo = photos_on_page[0]
            end_photo.click()
            time.sleep(2)
            mini_elements = self.browser.find_elements_by_class_name('wpO6b')
            button_like = mini_elements[1]
            button_like.click()

            self.liked_folowers += 1
        except:
            self.find_photos = False
            return


if __name__ == '__main__':
    user_login = 'nastya_pro_sugaring'
    user_password = 'fufik123567chupa'
    client_url = 'https://instagram.com/smile_shugar'
    # client_url = 'https://instagram.com/sugaring_vladikavkaz_anya/'
    # client_url = 'https://instagram.com/sweet_studio_vld/'

    # user_login = 'illi_homz'
    # user_password = 'badbalance166998'
    # client_url = 'https://instagram.com/smile_shugar'

    # user_login = 'diveev_studio'
    # user_password = '999ASDfgh'
    # client_url = 'https://instagram.com/domosdesign/'

    storris = SeeStorris(user_login, user_password, client_url)
    storris.run()


# кнопка кода класс: _5f5mN
# поле ввода класс: _281Ls
# Загрузка By4nA
