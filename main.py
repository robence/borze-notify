import requests

from lxml import html
from locale import str
from builtins import list, set, dict, range, print
from dotenv import load_dotenv
from pathlib import Path
import os
import datetime
from slack import WebClient
from slack.errors import SlackApiError
import time


env_path = Path(__file__).parent.absolute() / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
BASE_URL = 'http://borzeetterem.hu/'

client = WebClient(token=SLACK_API_TOKEN)


def send_slack(menu):
    channel = '#food'
    # text = "Börze: " + "\n" + menu[1] + "\n" + menu[2]

    try:
        client.chat_postMessage(channel=channel, text=menu)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def get_cafe_vian_menu(weekday):
    BASE_URL = 'https://www.cafevian.com/ebedmenue'
    session_requests = requests.session()

    # returns inner iframe url
    def parse_main_html():
        result = session_requests.get(BASE_URL)
        tree = html.fromstring(result.text)

        # get inner data url to fetch
        id_selector = '//div[@id="gaax5inlineContent-gridContainer"]'
        iframe_element = tree.xpath(id_selector + '/wix-iframe/iframe')[0]
        src_url = iframe_element.attrib['data-src']
        return src_url

    def parse_iframe_html(src_url):
        iframe_result = session_requests.get(src_url)
        iframe_tree = html.fromstring(iframe_result.text)
        return iframe_tree

    src_url = parse_main_html()
    iframe_tree = parse_iframe_html(src_url)

    # declare selectors
    div_selector = '//div[@id="mainDiv"]'
    place_selector = '/div/div/section/div/ul/li[3]'

    day_selector = div_selector + place_selector + \
        "/ul/li[" + str(weekday+1) + "]"
    main_course_selector = day_selector + '/div/div[2]'
    appetizer_selector = day_selector + '/ul/li/div/div/span'

    # menu information
    title = "Café Vian Bisztró"
    place = iframe_tree.xpath(div_selector + place_selector + "/h3")[0].text

    # day = iframe_tree.xpath(day_selector + '/div/div/div/span/span')[0].text
    main_course = iframe_tree.xpath(main_course_selector)[0].text
    appetizer = iframe_tree.xpath(appetizer_selector)[0].text

    def strip_text(x): return ' '.join(x.split()).replace("\uf077", "-")
    formatted_main_course = strip_text(main_course)

    menu = '%s | %s\n\n%s\n%s\n' % (
        title, place, formatted_main_course, appetizer)

    # print(day)
    return menu


def get_borze_menu(weekday):
    session_requests = requests.session()
    result = session_requests.get(BASE_URL)

    tree = html.fromstring(result.text)

    days = tree.xpath("/html/body/div/main/section[2]/div/div/h4")
    menus = tree.xpath("/html/body/div/main/section[2]/div/div/ul/li[1]/p")
    # nap = days[weekday].text
    eloetel = menus[weekday * 2].text
    masodik = menus[weekday * 2 + 1].text
    # menu = [nap, eloetel, masodik]
    title = 'Börze'

    menu = '%s\n\n%s\n%s\n' % (
        title, eloetel, masodik)
    return menu


def get_weekday():
    weekday = datetime.datetime.today().weekday()
    return weekday


def main():
    weekday = get_weekday()
    if weekday > 4:
        return

    menu1 = get_borze_menu(weekday)
    menu2 = get_cafe_vian_menu(weekday)
    print(menu1)
    print(menu2)
    send_slack(menu1)
    send_slack(menu2)


if __name__ == "__main__":
    main()
