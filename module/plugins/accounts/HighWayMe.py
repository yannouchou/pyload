# -*- coding: utf-8 -*-

from ..internal.misc import json
from ..internal.MultiAccount import MultiAccount


class HighWayMe(MultiAccount):
    __name__ = "HighWayMe"
    __type__ = "account"
    __version__ = "0.11"
    __status__ = "testing"

    __config__ = [("mh_mode", "all;listed;unlisted", "Filter hosters to use", "all"),
                  ("mh_list", "str", "Hoster list (comma separated)", ""),
                  ("mh_interval", "int", "Reload interval in hours", 12)]

    __description__ = """High-Way.me account plugin"""
    __license__ = "GPLv3"
    __authors__ = [("EvolutionClip", "evolutionclip@live.de"),
                   ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com")]

    API_URL = "https://high-way.me/api.php"

    def api_response(self, method, **kwargs):
        post=dict([(k.lstrip('_'), v) for k,v in kwargs.items()])
        json_data = self.load(self.API_URL,
                              get={method: ''},
                              post=post)
        return json.loads(json_data)

    def grab_hosters(self, user, password, data):
        json_data = self.api_response("hoster")

        return [element['name'] for element in json_data['hoster']]

    def grab_info(self, user, password, data):
        premium = False
        validuntil = -1
        trafficleft = None

        json_data = self.api_response("user")

        if 'premium' in json_data['user'] and json_data['user']['premium']:
            premium = True

        if 'premium_bis' in json_data['user'] and json_data['user']['premium_bis']:
            validuntil = float(json_data['user']['premium_bis'])

        if 'premium_traffic' in json_data['user'] and json_data['user']['premium_traffic']:
            # @TODO: Remove `/ 1024` in 0.4.10
            trafficleft = float(json_data['user']['premium_traffic']) / 1024

        return {'premium': premium,
                'validuntil': validuntil,
                'trafficleft': trafficleft}

    def signin(self, user, password, data):
        json_data = self.api_response("login", user=user, _pass=password)

        if not json_data.get('loggedin', False):
            self.fail_login()
