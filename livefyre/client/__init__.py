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

class LivefyreClient(Connection):
    """A simple client abstraction over python-rest-client:
       http://code.google.com/p/python-rest-client/
    """
    
    ROLES = ('owner', 'admin', 'banned', 'bozo', 'whitelist')
    _ROLE_PLURAL = dict(owner='owners', admin='admins', banned='banned', bozo='bozos', whitelist='whitelist')
    
    def __init__(self, domain, actor_token):
        Connection.__init__(self, "http://%s" % domain)
        self.actor_token = actor_token
        
    def create_site(self, url):
        return self.request("/sites/", "post", dict(url=url))
    
    def list_sites(self):
        return self.request("/sites/", "get")
    
    def add_role(self, role, jid, site_id=None):
        assert role in self.ROLES
        resource = "/%s/" % role
        if site_id:
            resource = "/site/%s%s" % (site_id, resource)
            
        return self.request(resource, "post", dict(jid=jid))
    
    def remove_role(self, role, jid, site_id=None):
        assert role in self.ROLES
        resource = "/%s/%s/" % (role, jid)
        if site_id:
            resource = "/site/%s%s" % (site_id, resource)

        return self.request(resource, "post", dict(jid=jid))
    
    def list_users(self, role, site_id=None):
        assert role in self.ROLES
        resource = "/%s/" % role
        if site_id:
            resource = "/site/%s%s" % (site_id, resource)

        return self.request(resource, "get")
    
    def register_profile_url(self, url):
        return self.request("/", "post", dict(pull_profile_url=url))
    
    def update_profile(self, user_id, user_data):
        return self.request("/profiles/", "post", 
                            dict(id=user_id), 
                            body=json.dumps(user_data),
                            header={'Content-Type':'application/json'})
                  
    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}, format='json'):
        #new_args = dict(client_id=self.client_id, client_secret=self.client_secret)
        new_args = dict(actor_token=self.actor_token)

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


# thread local client.
__thread_client = threading.local()

def get_client(url, client_id, client_secret):
    """Return a client for this thread."""
    key = "_" + hashlib.md5("%s:%s%s" % (url, client_id, client_secret)).hexdigest()
    if not getattr(__thread_client, key, None):
        setattr(__thread_client, key, Client(url, client_id, client_secret))
    return getattr(__thread_client, key)
