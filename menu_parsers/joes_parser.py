# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

from . import MenuParser
import requests
import lxml.html


class JoesParser(MenuParser):

    TIMEZONE = pytz.timezone('Europe/Zurich')
    MENSA_NAME = '*Joe's Popup*'

    def get_menu_string(self, timestamp):
        html_body = requests.get("https://www.joes-popup.ch/menuplan/").text
        root = lxml.html.fromstring(html_body)
        
        weekday = timestamp.weekday()
        menus = root.xpath('//div[@class="menu_content_classic"]')[-5:]
        menu_elem = menus[weekday]
        menu = self.MENSA_NAME + '\n' + menu_elem.xpath('div[@class="post_detail menu_excerpt"]')[0].text_content()

        return menu
        
