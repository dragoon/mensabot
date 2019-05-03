# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

from . import MenuParser
import requests
import lxml.html


class JoesParser(MenuParser):
    TIMEZONE = pytz.timezone('Europe/Zurich')
    MENSA_NAME = '*Joe\'s Popup*'

    def get_menu_string(self, timestamp: datetime):
        html_body = requests.get("https://www.joes-popup.ch/menuplan/").text
        root = lxml.html.fromstring(html_body)

        menu_contents = root.xpath('//div[@class="menu_content_classic"]')
        for menu_content in menu_contents:
            menu_title = menu_content.xpath('h5/span[@class="menu_title"]')
            if len(menu_title) > 0:
                if timestamp.strftime("%d.%m.%Y") in menu_title[0].text_content():
                    menu = self.MENSA_NAME + '\n' + menu_content.xpath('div[@class="post_detail menu_excerpt"]')[0].text_content()
                    return menu

        return ""
