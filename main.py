import sys
from fbchat import *
from fbchat import FBchatException, FBchatFacebookError, FBchatUserError
from secrets import *
import time


SESSION_COOKIES = None
AVAILABLE_ACTIONS = {
    1: 'Automatic Reactor'
}

def start():
    client = create_client()


def create_client():
    client = Client(email=email, password=password)
    client.setSession(client.getSession())
    return client


def check_login(client: Client):
    if not client.isLoggedIn():
        global SESSION_COOKIES
        # reinit client var using session cookies, or log in again
        try:
            client = Client(email=email, password=password, max_tries=2, session_cookies=SESSION_COOKIES)
        except FBchatException:
            print('Could not login...')
            sys.exit(0)
        return client
    return client


if __name__ == '__main__':
    start()
