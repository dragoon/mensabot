# -*- coding: utf-8 -*-
from datetime import datetime
import pytz

from . import MenuParser
import requests
import lxml.html


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

            menu = self.MENSA_NAME + '\n' + 'Not implemented yet'

            return menu
        except Exception as e:
            print(e)
        return self.MENSA_NAME + ": exception occurred"

