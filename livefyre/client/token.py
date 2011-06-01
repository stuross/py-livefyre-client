import hmac
import hashlib
from base64 import b64encode, b64decode
from datetime import datetime
import time

class LFAuthToken(object):
    """Class to create tokens for auth with Livefyre services."""
    def __init__(self, user, domain, key, duration=86400):
        self.data = self.populate_data(['auth', domain, user], duration)
        self.key = b64decode(key)
    
    def __str__(self):
        """Return the generated token string."""
        return self.token
    
    @property
    def token(self):
        """Create a signed token from inputs."""
        clientkey = bytearray(hmac.new(self.key, b"Client Key", hashlib.sha1).digest())
        
        # python 2.7 is pretty cool with bytearrays
        try:
                clientkey_sha1 = bytearray(hashlib.sha1(clientkey).digest())
                temp = bytearray(hmac.new(clientkey_sha1, self.data, hashlib.sha1).digest())
                sig = bytearray(x ^ y for x, y in zip(bytearray(temp), bytearray(clientkey)))
                ubase64sig = unicode(b64encode(sig))
                
        # python2.6 isn't. fail back to python2.6-style string semantics
        except TypeError, e:
                clientkey_sha1 = bytearray(hashlib.sha1(str(clientkey)).digest())
                temp = bytearray(hmac.new(str(clientkey_sha1), self.data, hashlib.sha1).digest())
                sig = bytearray(x ^ y for x, y in zip(bytearray(temp), bytearray(clientkey)))
                ubase64sig = unicode(b64encode(str(sig)))
                
        return b64encode(",".join([self.data, ubase64sig]))

    @classmethod
    def populate_data(cls, arg_list, duration=86400, now=None):
        """Create the right data input for Livefyre authorization."""
        if isinstance(now, datetime):
            now = now.utcnow().isoformat()
        tstamp = now if now else datetime.now().utcnow().isoformat()

        args = map(str, arg_list) #convert args to strings
        if filter(lambda x: (',' in x), arg_list):
            raise ValueError('Args can not contain comma (",") chars')
        values = ["lftoken", tstamp, duration] + arg_list
        data = ",".join((str(x) for x in values))
        return unicode(data)
        
