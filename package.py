# -*- coding = utf-8 -*-
# @Time: 2022/2/8 18:38
# @Author: Anshang
# @File: package.py
# @Software: PyCharm
import _thread
import os
import time
import uuid
import zipfile
from xml.dom import minidom


def makedir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)


def mimetype(path):
    with open(path + "/mimetype", "w") as f:
        f.write("application/epub+zip")


def container(path):
    with open(path + "/META-INF/container.xml", "w") as f:
        f.write(r"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
""")


def OEBPS(book):
    # makedir(path + "/OEBPS")

    title = book
    dom = minidom.Document()
    package_node = dom.createElement("package")
    package_node.setAttribute("version", "2.0")
    package_node.setAttribute("unique-identifier", "BookId")
    package_node.setAttribute("xmlns", "http://www.idpf.org/2007/opf")
    dom.appendChild(package_node)
    metadata = dom.createElement("metadata")
    metadata.setAttribute("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    metadata.setAttribute("xmlns:opf", "http://www.idpf.org/2007/opf")
    title_node = dom.createElement("dc:title")
    title_node.appendChild(dom.createTextNode(title))
    metadata.appendChild(title_node)
    format_node = dom.createElement("dc:format")
    format_node.appendChild(dom.createTextNode("Text/html(.xhtml,.html)"))
    metadata.appendChild(format_node)
    cover_node = dom.createElement("meta")
    cover_node.setAttribute("name", "cover")
    cover_node.setAttribute("content", "cover")
    metadata.appendChild(cover_node)
    package_node.appendChild(metadata)

    manifest = dom.createElement("manifest")
    images = os.listdir(book + "/OEBPS/Images")
    texts = os.listdir(book + "/OEBPS/Text")
    toc = dom.createElement("item")
    toc.setAttribute("id", "ncx")
    toc.setAttribute("href", "toc.ncx")
    toc.setAttribute("media-type", "application/x-dtbncx+xml")
    manifest.appendChild(toc)
    for img in images:
        item = dom.createElement("item")
        item.setAttribute("id", img)
        item.setAttribute("href", "Images/" + img)
        if img.split(".")[-1] == "jpg":
            item.setAttribute("media-type", "image/jpeg")
        else:
            item.setAttribute("media-type", "image/" + img.split(".")[-1])
        manifest.appendChild(item)
    for text in texts:
        item = dom.createElement("item")
        item.setAttribute("id", text)
        item.setAttribute("href", "Text/" + text)
        item.setAttribute("media-type", "application/xhtml+xml")
        manifest.appendChild(item)
    package_node.appendChild(manifest)

    spine = dom.createElement("spine")
    spine.setAttribute("toc", "ncx")
    for text in texts:
        item = dom.createElement("itemref")
        item.setAttribute("idref", text)
        spine.appendChild(item)
    package_node.appendChild(spine)

    with open(book + "/OEBPS/content.opf", "wb") as f:
        f.write(dom.toprettyxml(encoding="utf-8"))


def ncx(book):
    dom = minidom.Document()
    dom.appendChild(dom.createComment('DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN'))

    ncx_node = dom.createElement("ncx")
    ncx_node.setAttribute("xmlns", "http://www.daisy.org/z3986/2005/ncx/")
    ncx_node.setAttribute("version", "2005-1")

    head = dom.createElement("head")
    uid = dom.createElement("meta")
    uid.setAttribute("name", "dtb:uid")
    uid.setAttribute("content", "urn:uuid:" + str(uuid.uuid1()))
    head.appendChild(uid)
    depth = dom.createElement("meta")
    depth.setAttribute("name", "dtb:depth")
    depth.setAttribute("content", "2")
    head.appendChild(depth)
    page = dom.createElement("meta")
    page.setAttribute("name", "dtb:totalPageCount")
    page.setAttribute("content", "0")
    head.appendChild(page)
    max_page = dom.createElement("meta")
    max_page.setAttribute("name", "dtb:maxPageNumber")
    max_page.setAttribute("content", "0")
    head.appendChild(max_page)
    ncx_node.appendChild(head)

    doc_title = dom.createElement("docTitle")
    doc_title.appendChild(dom.createTextNode(book))
    ncx_node.appendChild(doc_title)

    nav_map = dom.createElement("navMap")
    texts = os.listdir(book + "/OEBPS/Text")
    count = 1
    for text in texts:
        point = dom.createElement("navPoint")
        point.setAttribute("id", "navPoint-" + str(count))
        point.setAttribute("playOrder", str(count))
        label = dom.createElement("navLabel")
        text_node = dom.createElement("text")
        text_node.appendChild(dom.createTextNode(text.split(".")[1]))
        label.appendChild(text_node)
        point.appendChild(label)
        content = dom.createElement("content")
        content.setAttribute("src", "Text/" + text)
        point.appendChild(content)
        nav_map.appendChild(point)
        count = count + 1
    ncx_node.appendChild(nav_map)

    dom.appendChild(ncx_node)

    with open(book + "/OEBPS/toc.ncx", "wb") as f:
        f.write(dom.toprettyxml(encoding="UTF-8", standalone=False))


def package(book, img_counter):
    mimetype(book)
    container(book)
    while True:
        time.sleep(1)
        if img_counter[0] == img_counter[1]:
            break
    OEBPS(book)
    ncx(book)
    os.chdir(book)
    epub = zipfile.ZipFile((book + ".epub"), 'w')
    epub.write("mimetype", compress_type=zipfile.ZIP_STORED)
    epub.write(r"META-INF\container.xml", compress_type=zipfile.ZIP_STORED)
    epub.write(r"OEBPS\content.opf", compress_type=zipfile.ZIP_STORED)
    epub.write(r"OEBPS\toc.ncx", compress_type=zipfile.ZIP_STORED)

    for dir in [r"OEBPS/Images", r"OEBPS/Text", r"OEBPS/Fonts", r"OEBPS/OEBPS", r"OEBPS/Styles"]:
        for f in os.listdir(dir):
            epub.write(os.path.join(dir, f), compress_type=zipfile.ZIP_STORED)
    epub.close()
    os.chdir("..")
