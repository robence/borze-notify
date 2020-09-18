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


env_path = Path(__file__).parent.absolute() / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
BASE_URL = 'http://borzeetterem.hu/'

client = WebClient(token=SLACK_API_TOKEN)


def send_slack(menu):
    channel = '#food'
    text = "Börze: " + "\n" + menu[1] + "\n" + menu[2]

    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def get_menu():
    weekday = datetime.datetime.today().weekday()

    if weekday > 4:
        return

    session_requests = requests.session()
    result = session_requests.get(BASE_URL)

    tree = html.fromstring(result.text)

    days = tree.xpath("/html/body/div/main/section[2]/div/div/h4")
    menus = tree.xpath("/html/body/div/main/section[2]/div/div/ul/li[1]/p")
    nap = days[weekday].text
    eloetel = menus[weekday * 2].text
    masodik = menus[weekday * 2 + 1].text
    menu = [nap, eloetel, masodik]
    return menu


def main():
    menu = get_menu()
    send_slack(menu)


if __name__ == "__main__":
    main()
