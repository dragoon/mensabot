# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

from . import MenuParser
import requests
import lxml.html


class SchanzeParser(MenuParser):

    TIMEZONE = pytz.timezone('Europe/Zurich')
    MENSA_NAME = '*Grosse Schanze*'

    def get_menu_string(self, timestamp):
        html_body = requests.get("http://www.grosseschanze.ch/restaurant/").text
        root = lxml.html.fromstring(html_body)
        tab_name = self._get_weekday_tab(timestamp)

        if not tab_name:
            return self.closed_string()

        for br in root.xpath("*//br"):
            br.tail = ", " + br.tail if br.tail else " "

        for div in root.xpath('//div[@class="lunchgate__category"]'):
            div.tail = ": "

        dishes = root.xpath('//div[@id="{}"]//div[@class="lunchgate__dish"]'.format(tab_name))
        menu = '\n'.join([d.text_content() for d in dishes])
        menu = self.MENSA_NAME + '\n' + menu

        return menu

    def _get_weekday_tab(self, timestamp: datetime):
        weekday = timestamp.weekday()
        if weekday == 0:
            return "tab-mo"
        elif weekday == 1:
            return "tab-di"
        elif weekday == 2:
            return "tab-mi"
        elif weekday == 3:
            return "tab-do"
        elif weekday == 4:
            return "tab-fr"
        return None
