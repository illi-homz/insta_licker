from selenium import webdriver
import os, time

PAGE_URL = 'file:///home/il/Загрузки/Страница не найдена • Instagram.html'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def check_on_error():
    browser = webdriver.Chrome(BASE_DIR + '/browser_drivers/chromedriver')
    time.sleep(2)
    browser.get(PAGE_URL)
    error_container = browser.find_element_by_class_name('error-container')
    error_title = error_container.find_element_by_tag_name('h2')
    error_body = error_container.find_element_by_tag_name('p')
    print(error_title.text)


if __name__ == '__main__':
    check_on_error()
