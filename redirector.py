import sys
import fbchat
import time
from twilio.rest import Client as tc
from secrets import account_sid_secret, auth_token_secret, twilio_phone, my_phone, email, password


USER_LIST = []          # list of users to redirect messages from
SESSION_COOKIES = None
TWILIO_CLIENT = None

# Redirects all messages to another platform, integrate twilio API
def start(ARGS):
    # run basic action-specific sanities
    redirector_sanity(ARGS)

    # create client
    client = None
    try:
        client = RedirectorBot(email=email, password=password, max_tries=1)
        global SESSION_COOKIES
        SESSION_COOKIES = client.getSession()
        client.setSession(SESSION_COOKIES)
    except fbchat.FBchatException as e:
        print('Could not login...\n{}'.format(e))
        sys.exit(0)

    # save list of approved users for redirection
    compile_users(ARGS, client)

    # create twilio client
    global TWILIO_CLIENT
    TWILIO_CLIENT = tc(account_sid_secret, auth_token_secret)

    # start listening, initiating event-driven hook
    if client is not None:
        client.listen()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print('Caught CTRL-C, exiting process')
                break

    graceful_exit(client)


def graceful_exit(client):
    if client is not None and client.isLoggedIn():
        client.logout()
        print('Logged out, goodbye!')

    sys.exit(0)


def redirector_sanity(ARGS):
    # handle no phone number input
    if ARGS.phone is None:
        print('Please supply a phone number with --phone')
        sys.exit(0)

    # handle correct formatting of phone number
    if ARGS.phone[0] != '+' or len(ARGS.phone) < 12:
        print('Please format the phone number in this fashion: +1AAABBBCCCC')
        sys.exit(0)

    # handle no --redirectusers
    if ARGS.users is None and ARGS.group is None:
        print('Please supply at least one user\'s or group\'s name to redirect messages from')
        sys.exit(0)


def trigger_redirect(self, message_object, thread_id):
    # construct message to send
    thread_name = None
    try:
        thread_name = self.fetchThreadInfo(thread_id)[thread_id].name
    except KeyError as e:
        thread_name = 'Unknown Thread Name'
    to_sent = 'FBReactor: {}\n{}'.format(thread_name, message_object.text)

    # finish twilio send...
    global TWILIO_CLIENT
    message = TWILIO_CLIENT.messages \
        .create(
        body=to_sent,
        from_=twilio_phone,
        to=my_phone
    )

    print(message.sid)


def compile_users(ARGS, client):
    global USER_LIST
    if ARGS.users is not None:
        for name in ARGS.users:
            try:
                user_id = client.searchForUsers(name=name)[0].uid
                USER_LIST.append(user_id)
            except IndexError as e:
                print('Could not find desired user: {}, skipping...'.format(name))
                continue
            except fbchat.FBchatException as e:
                print('API Error')
                continue
    elif ARGS.group is not None:
        try:
            group_id = (client.searchForGroups(name=ARGS.group)[0]).uid
            USER_LIST.append(group_id)
        except fbchat.FBchatException as e:
            print('Could not find desired group: {}, exiting...'.format(ARGS.group))
            graceful_exit(client)
    else:
        print('No user / group indicated to redirect messages from...')
        graceful_exit(client)


class RedirectorBot(fbchat.Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        # self.markAsRead(thread_id)        # test to not send read receipts

        # If user did not send message, redirect accordingly
        if author_id != self.uid and (thread_id in USER_LIST or author_id in USER_LIST):
            trigger_redirect(self, message_object, thread_id)
