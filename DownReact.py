import sys
from fbchat import *


class DownReactor(Client):
    def onMessage(self, mid, author_id, message_object, thread_id, thread_type, ts, metadata, msg, **kwargs):
        # Do something with message_object here
        pass
