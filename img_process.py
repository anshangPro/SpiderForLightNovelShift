# -*- coding = utf-8 -*-
# @Time: 2022/2/8 13:58
# @Author: Anshang
# @File: img_process.py
# @Software: PyCharm
import _thread

import requests
import re

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 Edg/97.0.1072.76"
headers = {
    "User-Agent": UA,
}


def download(url, book_name, changed_url, img_counter):
    img_file = requests.get(url, headers=headers).content
    with open(book_name + "/OEBPS" + changed_url, "wb") as f:
        f.write(img_file)
        f.close()
    # print(book_name, "pic", img_counter[1], "download finish")
    img_counter[1] = img_counter[1] + 1


img_re = re.compile(r"<img.*?>")
url_re = re.compile(r'src="(?P<url>.*?)"')


def img_process(src, img_counter,book_name=None):
    imgs = img_re.finditer(src)
    for img in imgs:
        url = url_re.search(img.group()).group("url")
        file_name = url.split('/')[-1]
        changed_url = "/Images/" + file_name
        src = src.replace(url, ".."+changed_url)
        img_counter[0] = img_counter[0] + 1
        if url.startswith("/"):
            url = "https://www.lightnovel.app" + url
        _thread.start_new_thread(download, (url, book_name, changed_url, img_counter))
    return src

