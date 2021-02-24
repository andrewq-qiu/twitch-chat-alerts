"""
Run this file to open the bot.
Change the contents of if __name__ == '__main__'
to change bot behaviour for testing purposes. For example,
you may call test_beeps_and_browser() to see how loud the notification is.

Change the contents of properties.yml to
change the runtime behaviour of the bot.

This script is licensed by the MIT License.
See LICENSE for more information.
"""

import yaml
import pathlib
import socket
import logging
import webbrowser
from playsound import playsound
import datetime
import threading as th

logging.basicConfig(level=logging.DEBUG)


def load_properties() -> dict:
    # Project root directory
    root = ROOT

    with open(root + '\properties.yml', 'r') as f:
        data = yaml.safe_load(f)

        logging.info('Loaded ' + root + '\properties.yml')

        logging.info('Found the following keywords: ')
        keywords = '\nl - '.join(
            f'({", ".join(kw for kw in kw_set["required"].split())}) opens {kw_set["open"]}'
            for kw_set in data['keywords'])
        logging.info(keywords)

        return data


def test_beeps_and_browser():
    webbrowser.open('https://google.ca')
    playsound(ROOT + '\\' + PROPERTIES['notify']['sound'])


def alert(kw_set: dict[str, str]):
    webbrowser.open(kw_set['open'])
    playsound(ROOT + '\\' + PROPERTIES['notify']['sound'])


KEEP_RUNNING = True


def keyboard_thread_init():
    thread = th.Thread(target=keyboard_thread, args=())
    thread.start()


def keyboard_thread():
    global KEEP_RUNNING

    while True:
        x = input('To escape back to the main screen, enter "q": \nl')

        if x == 'q':
            KEEP_RUNNING = False
            return


def run_bot():
    # Create new thread for keyboard
    keyboard_thread_init()

    while KEEP_RUNNING:
        resp = SOCK.recv(2048).decode('utf-8')
        if len(resp) == 0:
            # Ignore message
            pass
        # Twitch will send you a PING which you
        # will have to respond with every 5 mins
        elif resp.startswith('PING'):
            SOCK.send("PONG\n".encode('utf-8'))
        else:

            for kw_set in PROPERTIES['keywords']:
                keywords_match = all(req in resp
                                     for req in kw_set['required'].split())

                if keywords_match:
                    alert(kw_set)

            log_text = datetime.datetime.now().strftime('%H:%M:%S ') + resp
            logging.info(log_text)


def interface():
    """The main UI for accessing tests and bot functionality from command line"""
    global KEEP_RUNNING

    while True:
        x = input('Enter "test" to test sounds or "run" to run the bot: ')
        if x == 'test':
            test_beeps_and_browser()
        elif x == 'run':
            logging.info('Press "q" to return back to this menu.')
            KEEP_RUNNING = True
            run_bot()
        elif x == 'q':
            logging.info('Aborting the script...')
            return


# Load Properties
ROOT = str(pathlib.Path(__file__).parent.absolute())
PROPERTIES = load_properties()

# Connect to socket
SOCK = socket.socket()
SOCK.connect((PROPERTIES['socket']['url'], PROPERTIES['socket']['port']))

# Send information on where to connect
SOCK.send(f"PASS {PROPERTIES['login']['token']}\n".encode('utf-8'))
SOCK.send(f"NICK {PROPERTIES['login']['nickname']}\n".encode('utf-8'))
SOCK.send(f"JOIN {PROPERTIES['login']['channel']}\n".encode('utf-8'))

if __name__ == '__main__':
    breakpoint()
    interface()
    pass
