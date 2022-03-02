# -*- coding = utf-8 -*-
# @Time: 2022/1/31 12:50
# @Author: Anshang
# @File: lightShiftSpider.py
# @Software: PyCharm
import _thread
import re

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import os
from text_decode import format
from img_process import img_process
from package import package

EMAIL = ""
PASSWORD = ""
max_time = 10

web = Chrome()
login_token = ""
login_js_head = """const DATA_BASE = 'eBook_Shelf';
let db = {};
const request = window.indexedDB.open(DATA_BASE, 6);
request.onupgradeneeded = function(event) {
    db = event.target.result;
    const objectStore = db.createObjectStore('USER_AUTHENTICATION');
    objectStore.transaction.oncomplete = function(event) {
        const transaction = db.transaction(['USER_AUTHENTICATION'], 'readwrite');
        const objStore = transaction.objectStore('USER_AUTHENTICATION');
        objStore.add('"""
login_js_tail = """', 'RefreshToken');
    };
}"""
login_js = login_token.join((login_js_head, login_js_tail))


def if_refresh(content):
    refresh = False
    try:
        content.getTagName()
    except Exception as e:
        refresh = True
    return


def get_element(by, locate, element=None):
    try:
        element = WebDriverWait(web, max_time).until(EC.presence_of_element_located((by, locate)))
    except Exception as msg:
        print("failed to find %s" % locate)
    return element


head_a = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>'''
head_b = '''</title>
</head>
<body><div>'''

end = r'''</div></body>
</html>'''


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def makedir(book):
    mkdir(book)
    mkdir(book + "/META-INF")
    mkdir(book + "/OEBPS")
    mkdir(book + "/OEBPS/Fonts")
    mkdir(book + "/OEBPS/Images")
    mkdir(book + "/OEBPS/OEBPS")
    mkdir(book + "/OEBPS/Styles")
    mkdir(book + "/OEBPS/Text")


img_counter = [0, 0]


def sub_thread(book_name, counter, pop_log, text):
    pop_log = pop_log.replace('/', '、')
    with open("%s/OEBPS/Text/%03d.%s.html" % (book_name, counter, pop_log), "w", encoding='utf-8') as file:
        file.write(pop_log.join((head_a, head_b)))
        file.write(img_process(format(text), img_counter,  book_name=book_name))
        file.write(end)


def download(url):  # web.get((By.ID, 'data-v-675005fb'))
    web.get(url)
    start_time = time.time()
    book_name = ''
    while True:
        book_name = get_element(By.XPATH,
                                '/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div[2]/div/div[2]').get_attribute(
            'innerHTML')
        if book_name == '':
            time.sleep(0.1)
        else:
            break
    name = re.search("《(?P<name>.*)》", book_name)
    if name != None:
        name = name.group("name")
    if name is not None:
        book_name = name
    print("start book", book_name)
    makedir(book_name)
    counter = 0
    get_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[2]/a[1]").click()
    while True:
        counter = counter + 1
        button = get_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[1]/div[3]/button[3]/span[2]")
        if button.get_attribute('innerHTML') != "下一章":
            print("Finish book(%s)\nTime cost: %.2f" % (url, time.time() - start_time))
            break
        else:
            text = get_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div[2]/div').get_attribute(
                'innerHTML')
            pop_log = web.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/div/div/div[1]/div").get_attribute(
                'innerHTML')
            try:  # to get the last log
                test = 0
                while True:
                    test = test + 1
                    pop_log = web.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/div[{0}]/div/div[1]/div".format(
                        test)).get_attribute('innerHTML')
            except Exception:
                pass
            if pop_log != "已经是最后一页了":
                sub_thread(book_name, counter, pop_log, text)
                button.click()
            else:
                package(book_name, img_counter)
                print("book {0} finish, cost time {1}".format(book_name, time.time() - start_time))
                break
            time.sleep(1)


def login():
    email = get_element(
        By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[2]/form/label[1]/div/div[1]/div[2]/input')
    email.send_keys(EMAIL)
    password = get_element(
        By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[2]/form/label[2]/div/div[1]/div[2]/input')
    password.send_keys(PASSWORD)
    get_element(
        By.XPATH, '/html/body/div[1]/div/div[2]/div/div/div[1]/div/div[2]/form/button').click()
    finish_time = time.time()
    while True:
        print(web.current_url)
        if not web.current_url.startswith("https://next.acgdmzy.com/login"):
            print("Successfully login")
            break
        if time.time() - finish_time > 5:
            print("login failed")
            exit()


def login_with_token():
    web.get('https://www.lightnovel.app')
    web.execute_script(login_js)
    time.sleep(0.3)


if __name__ == "__main__":
    login_with_token()
    for i in range(10225, 10226):
        download("https://www.lightnovel.app/book/info/%d" % i)
    web.close()
