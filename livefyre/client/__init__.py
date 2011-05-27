from restful_lib import Connection
from httplib2 import HttpLib2Error
import threading
import urllib
import json

from logging import getLogger

LOG = getLogger(__name__)
        
class RemoteError(Exception): 
    """Generic remote exception"""
    pass

class NotFoundError(RemoteError): pass

class ServerError(RemoteError): pass

class BadRequestError(RemoteError): pass

class AuthenticationError(RemoteError): pass

class Client(Connection):
    """A simple client connection to a Capture server extending python-rest-client:
       http://code.google.com/p/python-rest-client/
    """
    def __init__(self, url, client_id, client_secret):
        Connection.__init__(self, url)
        self.client_id = client_id
        self.client_secret = client_secret
                  
    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}, format='json'):
        new_args = dict(client_id=self.client_id, client_secret=self.client_secret)

        LOG.debug("%s: %s?%s headers=%s", 
                  method, resource, urllib.urlencode(args if args else {}), str(headers))  

        if args:
            new_args.update(args)
      
        resp = Connection.request(self, resource, method=method, args=new_args, body=body, filename=filename, headers=headers)
        status = resp['headers']['status']
        msg = resp['body']
        if status == '200' and format == 'json':
            try:
                resp['body'] = json.loads(resp['body'])
                status = resp['body'].get('code')
                msg = resp['body'].get('error')
            except ValueError, e:
                raise RemoteError("Server responded with bad json: %s" % (e, resp['body']))

        if status == '404':
            raise NotFoundError(resource)
        elif status.startswith('5'):
            raise ServerError(msg)
        elif status == '400':
            raise BadRequestError(msg)
        elif status == '401':
            raise AuthenticationError(msg)
        elif status == '403':
            raise PermissionError(msg)

        return resp['body']

    def ping(self):
        return self.request("/", format="html")
