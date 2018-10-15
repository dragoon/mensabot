# -*- coding: utf-8 -*-
from datetime import datetime

import pdfminer.high_level
import pdfminer.layout
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
            outfp = io.StringIO()
            laparams = pdfminer.layout.LAParams()
            laparams.detect_vertical = True
            pdfminer.high_level.extract_text_to_fp(input_fp, outfp, laparams=laparams)

            menu_string = outfp.getvalue()

            menu = self.MENSA_NAME + '\n' + menu_string

            return menu
        except Exception as e:
            print(e)
        return self.MENSA_NAME + ": exception occurred"

