import sys
import fbchat
import twilio
from secrets import account_sid_secret, auth_token_secret, twilio_phone, my_phone

# Redirects all messages to another platform, integrate twilio API
def start(ARGS):
    redirector_sanity(ARGS)


def redirector_sanity(ARGS):
    if ARGS.phone is None:
        print('Please supply a phone number')


'''
    message = client.messages \
            .create(
                 body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                 from_='+15017122661',
                 to='+15558675310'
             )
    
    print(message.sid)
'''
