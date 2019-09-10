import sys
import fbchat
from secrets import *
from reactor import REACTS
import argparse
import time


SESSION_COOKIES = None

AVAILABLE_ACTIONS = {
    1: 'Automatic Reactor',
    2: 'Twilio Redirector',
}


def start():
    # conditions to handle action-specific sanitizations and launch new control flow
    if ARGS.action == 1:
        import reactor
        reactor.start(ARGS)
    elif ARGS.action == 2:                # Expand as new actions are incorporated
        import redirector
        redirector.start()
    sys.exit(0)


def create_client():
    try:
        client = fbchat.Client(email=email, password=password, max_tries=1)
        global SESSION_COOKIES
        SESSION_COOKIES = client.getSession()
        client.setSession(SESSION_COOKIES)
        return client
    except fbchat.FBchatException as e:
        print('Could not login...\n{}'.format(e))
    sys.exit(0)


def check_login(client):            # aux method to be used throughout codebase
    if not client.isLoggedIn():
        global SESSION_COOKIES
        # reinit client var using session cookies, or log in again
        try:
            new_client = fbchat.Client(email=email, password=password, max_tries=1, session_cookies=SESSION_COOKIES)
        except fbchat.FBchatException:
            print('Could not login...')
            sys.exit(0)
        return new_client
    return client


def get_args():
    parser = argparse.ArgumentParser(description='Facebook Messenger Chat Client')

    # Group / User switch
    recipient = parser.add_argument_group(title='Recipient')
    recipient.add_argument('--user', help='Pass in Facebook username of individual. Mutually exclusive with --group.',
                           default=None)
    recipient.add_argument('--group', help='Pass in Facebook group chat name. Mutually exclusive with --user.',
                           default=None)

    # Action switch
    actions = parser.add_argument_group(title='Action')
    actions.add_argument('-a', '--action', required=False, type=int,
                         help='Select number to allocate action to this instance of FBReactor\n{}'.format(
                             AVAILABLE_ACTIONS))

    # Action Options switch
    action_options = parser.add_argument_group(title='Action Options',
                                               description='Read documentation to know which options are necessary for '
                                                           'an action')
    # Reactor Action Options
    action_options.add_argument('--reactor', default=None, help='Specify the react you would like to do:\n{}'
                                .format(list(REACTS.keys())))

    action_options.add_argument('--phone', default=None,
                                help='Specify the phone number you would like messages to redirect to')

    return parser.parse_args()


def general_sanity():
    # check that not both --user and --group is passed in
    if ARGS.user is not None and ARGS.group is not None:
        print('Please only specify either --user or --group, not both.')
        sys.exit(0)


def check_recipient():      # aux method to be used when sending/interacting with a message
    # check that user provided exists within CLIENT's network
    if ARGS.user is not None:
        pass
    # check that group provided exists within CLIENT's network
    elif ARGS.group is not None:
        pass


if __name__ == '__main__':
    # parse arguments
    ARGS = get_args()

    # run sanitization of arguments (generalized, not action-specific)
    general_sanity()

    # create client if no action is specified, and log the user in:
    if ARGS.action is None:
        print('No action selected, simply logging in...')
        CLIENT = create_client()
        while True:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                print('Logging out...')
                # graceful exit
                if CLIENT.isLoggedIn():
                    CLIENT.logout()
                    print("Logged out, goodbye!")

    # handle action-specific sanities and launch new control flow
    start()
