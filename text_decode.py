# -*- coding = utf-8 -*-
# @Time: 2022/2/7 12:54
# @Author: Anshang
# @File: text_decode.py
# @Software: PyCharm

# \u3002 should be avoided
# other less than \ue000 should be deleted
import re
import json

string = """燕削竟終點绩絮坡。圓游間內，肛函急乾跨挥─宾─兽從络糙變囤為听盔勇勾輕最导窜啪。
逛傲童讽莫圍览恳闷帶园恤膝鹰銳紅，張渺咖月绊元摘恬們漱哲郎。
"""
char_set = json.loads(open("out.json", "r", encoding="utf-8").read())
reversed_set = json.loads(open("reverse.json", "r", encoding="utf-8").read())
text_set = json.loads(open("text.json", "r", encoding="utf-8").read())
blank_set = json.loads(open("blank.json", "r", encoding="utf-8").read())


def is_valid(char):
    index = str(ord(char))
    if index in text_set:
        if index in blank_set:
            return False
        return True
    return True
    # try:
    #     blank_set[index]
    #     return True
    # except KeyError:
    #     return False
    # # index = ord(char)
    # if 0xe000 > index > 128 and index != 0x3002 and not 12289 < index < 12319 and not 8544 < index < 8555 and not 8560 < index < 8569 and not 9312 < index < 9839:
    #     return False
    # return True


def format(string):
    res = ""
    for s in string:
        if is_valid(s):
            try:
                # print(s, char_set[str(ord(s))])
                res = res + char_set[str(ord(s))]
            except KeyError:
                res = res + s
    return res


def main():
    f = open("《當蠢蛋FPS玩家誤闖異世界之時 1》/5.第一章.html", "r", encoding="utf-8")
    print(format(f.read()))
    print(format(string))
    # with open("reverse.json", "w", encoding="utf_8") as f:
    #     f.write("{")
    #     for i in char_set:
    #         if char_set[i] != "":
    #             f.write('"{0}": "{1}",\n'.format(char_set[i], i))
    #     f.write("}")


if __name__ == "__main__":
    main()
