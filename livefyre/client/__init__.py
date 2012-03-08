from restful_lib import Connection
from httplib2 import HttpLib2Error
import threading
import urllib
import json
import datetime, time
from .token import LFAuthToken

from logging import getLogger

LOG = getLogger(__name__)

class RemoteError(Exception):
    """Generic remote exception"""
    pass

class NotFoundError(RemoteError): pass

class ServerError(RemoteError): pass

class ConnectionError(RemoteError): pass

class BadRequestError(RemoteError): pass

class AuthenticationError(RemoteError): pass

class PermissionError(RemoteError): pass

class LivefyreClient(Connection):
    """A simple client abstraction over python-rest-client:
       http://code.google.com/p/python-rest-client/
    """

    def __init__(self, domain, domain_key, endpoint=None, user="system", timeout=5, cache_dir=".cache"):
        if not endpoint:
            endpoint = "http://%s" % domain
        Connection.__init__(self, endpoint)
        self.domain = domain
        self.domain_key = domain_key
        self.user = user
        self.timeout=timeout

    def create_site(self, url):
        return self.request("/sites/", "post", dict(url=url))

    def list_sites(self):
        return self.request("/sites/", "get")

    def add_role(self, role, user_id, site_id=None):
        resource = self._role_resource_path(role, site_id=site_id, user_id=user_id)
        return self.request(resource, "get", args={'_method': 'PUT'})

    def remove_role(self, role, user_id, site_id=None):
        resource = self._role_resource_path(role, site_id=site_id, user_id=user_id)
        return self.request(resource, "get", args={'_method': 'DELETE'})

    def list_users(self, role, site_id=None):
        resource = self._role_resource_path(role, site_id=site_id, user_id=None)
        return self.request(resource, "get")

    def register_profile_url(self, url):
        return self.request("/", "post", dict(pull_profile_url=url))

    def get_profile_data(self, profile_id):
        return self.request("/profile/%s/" % profile_id, "get")['data']

    def get_profile_comments(self, profile_id, comment_offset):
        return self.request("/profile/%s/comments/%d/" % (profile_id, comment_offset), "get")['data']

    def update_profile(self, user_id, user_data):
        return self.request("/profiles/", "post",
                            dict(id=user_id, data=json.dumps(user_data)), )
                            
    def delete_profile(self, user_id):
        return self.request("/profile/%s/" % user_id,
                            "GET", args={'_method': 'DELETE'})
        
    def comment_counts(self, since=None, to=None):
        since = _convert_to_epoch(since, int(time.mktime((datetime.datetime.now() - datetime.timedelta(hours=24)).utctimetuple())))
        to = _convert_to_epoch(to, None)
        
        args = {'from': since}
        if to:
            args['to'] = to
            
        return self.request("/conversations/metrics/counts", "get", args)

    """Which roles"""
    ROLES = ('owner', 'admin', 'outcast', 'member')
    ROLE_PLURALS = dict(owner='owners', admin='admins', outcast='outcasts', member='members')

    def _role_resource_path(self, role, user_id=None, site_id=None):
        assert role in self.ROLES
        resource = []
        if site_id:
            resource.append('site')
            resource.append(site_id)
        if user_id:
            jid = "%s@%s" % (user_id, self.domain)
            resource.append(role)
            resource.append(jid)
        else:
            resource.append(self.ROLE_PLURALS[role])

        return "/" + "/".join(map(str, resource)) + "/"

    def request(self, resource, method = "get", args = None, body = None, filename=None, headers={}, format='json'):
        new_args = dict(actor_token=self.auth_token)
        new_headers = dict(Host=self.domain)
        if headers:
            new_headers.update(headers)

        LOG.debug("%s: %s?%s headers=%s",
                  method, resource, urllib.urlencode(args if args else {}), str(new_headers))

        if args:
            new_args.update(args)

        try:
            resp = Connection.request(self, resource, method=method.lower(), args=new_args, body=body, filename=filename, headers=new_headers)
        except AttributeError, e:
            # http://code.google.com/p/httplib2/issues/detail?id=152
            if 'makefile' not in e:
                raise ConnectionError("Server is unavailable")

        status = resp['headers']['status']
        msg = resp['body']
        if status == '200' and format == 'json':
            try:
                resp['body'] = json.loads(resp['body'])
            except ValueError, e:
                raise RemoteError("Server responded with bad json: %s" % (e, resp['body']))

            if type(resp['body']) == dict:
                try:
                    status = resp['body']['code']
                    msg = resp['body']['error']
                except KeyError:
                    pass

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

    @property
    def auth_token(self):
        return LFAuthToken(self.user, self.domain, self.domain_key).token

def _convert_to_epoch(v, default=None):
    ov = v
    if type(v) in (int, float):
        v = int(v)
    elif type(v) == datetime.datetime:
        v = int(time.mktime(v.utctimetuple()))
    elif v is None:
        v = default
    else:
        assert False, "Unable to convert object to epoch time %s" % v
        
    return v
