# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Dict

import PyPDF2
import re
import pytz
import io
import requests
import lxml.html

from . import MenuParser


class HofliParser(MenuParser):

    TIMEZONE = pytz.timezone('Europe/Zurich')
    MENSA_NAME = '*Bärenhöfli*'

    def get_menu_string(self, timestamp):
        try:
            html_body = requests.get("http://baerenhoefli.ch/").text
            root = lxml.html.fromstring(html_body)
            # find the link to the menu

            menu_link = root.xpath('//div[@id="daily-menu"]/a')[0].attrib['href']
            pdf = requests.get(menu_link)
            input_fp = io.BytesIO(pdf.content)
            pdf_reader = PyPDF2.PdfFileReader(input_fp)

            page = pdf_reader.getPage(0)
            text = page.extractText()
            text = text[19:]
            text = re.sub(r'(?=[^\s\)])([A-Z][a-z])', ' \g<1>', text)
            text = text.replace(',', '')
            menus = parse_first_page(text)

            menu = self.MENSA_NAME + '\n' + get_menu_for_weekday(timestamp, menus)

            return menu
        except Exception as e:
            print(e)
        return self.MENSA_NAME + ": exception occurred"


def get_menu_for_weekday(timestamp: datetime, menus: Dict[str, Dict]):
    weekday = timestamp.weekday()
    menu = None
    if weekday == 0:
        menu = menus['Montag']
    elif weekday == 1:
        menu = menus['Donnerstag']
    elif weekday == 2:
        menu = menus['Dienstag']
    elif weekday == 3:
        menu = menus['Mittwoch']

    if menu is None:
        return 'No menu for today!'

    menu_string = 'Daily: {}, {} CHF\nBusinesslunch: {}, {} CHF'.format(menu['daily'], menu['daily_price'],
                                                                menu['menu'], menu['price'])
    return menu_string


def parse_first_page(text: str):
    menu_queue = []

    menu_started = False
    next_price = False

    menus = {}

    days = {'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag'}
    for word in text.split():
        if word.endswith("CHF") and menu_started:
            menu_queue[0]['menu'].append(word[:-3])
            next_price = True
            continue

        if word in days:
            menu_queue.append({"day": word, "menu": []})
            continue

        if word.startswith("Businesslunch"):
            menu_queue[0]['daily'] = ' '.join(menu_queue[0]['menu'])
            menu_queue[0]['daily_price'] = menu_queue[0]['price']
            menu_queue[0]['menu'] = [word[len("Businesslunch"):]]
            continue

        if word.endswith("***"):
            menu_queue[0]['menu'].append(word[:-3] + ',')
            menu_started = True
            continue

        if next_price:
            menu_queue[0]['price'] = word
            next_price = False
            continue

        if word == "Businessdessert":
            menu_started = False
            menu_queue[0]['menu'] = ' '.join(menu_queue[0]['menu'])
            day = menu_queue[0]['day']
            menus[day] = menu_queue.pop(0)
            continue

        if menu_started:
            menu_queue[0]['menu'].append(word)
    return menus


if __name__ == "__main__":

    print(HofliParser().get_menu_string(datetime.now()))

