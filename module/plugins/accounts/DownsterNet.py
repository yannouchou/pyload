# -*- coding: utf-8 -*-

import string
import random
import time

import pycurl
from module.network.HTTPRequest import BadHeader

from ..internal.misc import json
from ..internal.MultiAccount import MultiAccount


class DownsterApi(object):
    API_URL = "https://downster.net/api/"

    def __init__(self, plugin):
        self.plugin = plugin

        if hasattr(self.plugin, 'account'):
            self.account_plugin = self.plugin.account

        else:
            self.account_plugin = self.plugin

    def api_request(self, method, get={}, **kwargs):
        self.plugin.req.http.c.setopt(pycurl.HTTPHEADER, [
            "Accept: application/json, text/plain, */",
            "Content-Type: application/json",
            "X-Flow-ID: " + self.flow_id(),
        ])
        self.plugin.req.http.c.setopt(pycurl.USERAGENT,
                                      "User-Agent: pyLoad/" + self.plugin.pyload.version +
                                      " DownsterNet/" + self.account_plugin.__version__)

        try:
            res = self.plugin.load(self.API_URL + method,
                                   get=get,
                                   post=json.dumps(kwargs))
        except BadHeader, e:
            res = e.content

        res = json.loads(res)

        return res

    def rnd(self):
        return ''.join([random.choice(string.ascii_lowercase + string.digits) for n in range(5)])

    def flow_id(self):
        user_flow_id = self.account_plugin.info['data'].get('user_flow_id')
        self.plugin.log_debug("User flow id: %s" % user_flow_id)
        if not user_flow_id:
            self.account_plugin.info['data']['user_flow_id'] = self.rnd()
            self.plugin.log_info('Created user flow id: %s' % self.account_plugin.info['data']['user_flow_id'])

        return 'PYL_' + self.account_plugin.info['data']['user_flow_id'] + '_' + self.rnd()


class DownsterNet(MultiAccount):
    __name__ = "DownsterNet"
    __type__ = "account"
    __version__ = "0.02"
    __status__ = "testing"

    __config__ = [("mh_mode", "all;listed;unlisted", "Filter hosters to use", "all"),
                  ("mh_list", "str", "Hoster list (comma separated)", ""),
                  ("mh_interval", "int", "Reload interval in hours", 12)]

    __description__ = """Downster.net account plugin"""
    __license__ = "GPLv3"
    __authors__ = [(None, None)]

    api = None

    def grab_hosters(self, user, password, data):
        api_data = self.api.api_request("download/usage")
        if not api_data['success']:
            self.log_error('Could not get hoster info: ' + api_data['error'])
            return []

        else:
            return [hoster['hoster'] for hoster in api_data['data']]

    def grab_info(self, user, password, data):
        api_data = self.api.api_request("user/info")

        if not api_data['success']:
            validuntil = None
            trafficleft = None
            premium = False

            self.log_error('Could not get user info: ' + api_data['error'])

        else:
            validuntil = time.mktime(time.strptime(api_data['data']['premiumUntil'], "%Y-%m-%dT%H:%M:%S.%f+00:00"))
            trafficleft = -1
            premium = validuntil > time.time()

        return {'validuntil': validuntil,
                '': trafficleft,
                'premium': premium}

    def signin(self, user, password, data):
        if self.api is None:
            self.api = DownsterApi(self)

        api_data = self.api.api_request('user/info')
        if api_data['success']:
            self.skip_login()

        api_data = self.api.api_request("user/authenticate",
                                        email=user,
                                        password=password)

        if not api_data['success']:
            self.fail_login(api_data['error'])
