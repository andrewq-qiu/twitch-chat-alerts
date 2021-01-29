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

logging.basicConfig(level=logging.DEBUG)


def load_properties() -> dict:
    # Project root directory
    root = ROOT

    with open(root + '\properties.yml', 'r') as f:
        data =  yaml.safe_load(f)
        data['keywords']['req'] = data['keywords']['required'].split()
        return data


def test_beeps_and_browser():
    webbrowser.open(PROPERTIES['notify']['open'])
    playsound(ROOT + '\\' + PROPERTIES['notify']['sound'])


def run_bot():
    try:
        while True:
            resp = SOCK.recv(2048).decode('utf-8')
            if len(resp) == 0:
                # Ignore message
                pass
            # Twitch will send you a PING which you
            # will have to respond with every 5 mins
            elif resp.startswith('PING'):
                SOCK.send("PONG\n".encode('utf-8'))
            else:
                keywords_match = all(req in resp
                                     for req in PROPERTIES['keywords']['req'])
                if keywords_match:
                    webbrowser.open(PROPERTIES['notify']['open'])
                    playsound(ROOT + '\\' + PROPERTIES['notify']['sound'])
                    logging.warning(resp)
                elif PROPERTIES['notify']['print_all']:
                    logging.info(resp)

    except KeyboardInterrupt:
        print('Program interrupted! Re-run again')


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
    run_bot()
    # test_beeps_and_browser()
    pass
