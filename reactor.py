import sys
from fbchat import *
from fbchat import MessageReaction, FBchatException
from secrets import *
import time

REACTS = {
    'heart': MessageReaction.LOVE,
    'wow': MessageReaction.WOW,
    'mad': MessageReaction.ANGRY,
    'sad': MessageReaction.SAD,
    'haha': MessageReaction.SMILE,
    'up': MessageReaction.YES,
    'down': MessageReaction.NO,
}

CHOSEN_REACT = None
SESSION_COOKIES = None


def start(ARGS):
    # action specific sanity
    reactor_sanity(ARGS)

    # setting global var to user-desired reaction
    global CHOSEN_REACT
    CHOSEN_REACT = ARGS.reactor

    # initiating custom client
    client = None
    try:
        client = AutoReactor(email=email, password=password, max_tries=1)
        global SESSION_COOKIES
        SESSION_COOKIES = client.getSession()
        client.setSession(SESSION_COOKIES)
    except FBchatException as e:
        print('Could not login...\n{}'.format(e))
        sys.exit(0)

    # initiating event-driven hook
    if client is not None:
        client.listen()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print('Caught CTRL-C, exiting process')

    # graceful exit
    if client is not None and client.isLoggedIn():
        client.logout()
        print('Logged out, goodbye!')

    sys.exit(0)


def reactor_sanity(ARGS):
    # handle no reactor switch
    if ARGS.reactor is None:
        print('Please specify a --reactor option with one of the following:\n{}'.format(list(REACTS.keys())))
        sys.exit(0)

    # handle incorrect react option
    if ARGS.reactor not in list(REACTS.keys()):
        print('Please specify a --reactor option with one of the following:\n{}'.format(list(REACTS.keys())))
        sys.exit(0)


class AutoReactor(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        # self.markAsRead(thread_id)        # test to not send read receipts

        # If user did not send message, react accordingly
        if author_id != self.uid:
            self.reactToMessage(message_id=message_object, reaction=REACTS[CHOSEN_REACT])
