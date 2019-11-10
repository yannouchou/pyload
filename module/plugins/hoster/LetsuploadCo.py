# -*- coding: utf-8 -*-

import os
import re

from ..internal.SimpleHoster import SimpleHoster


class LetsuploadCo(SimpleHoster):
    __name__ = "LetsuploadCo"
    __type__ = "hoster"
    __version__ = "0.02"
    __status__ = "testing"

    __pattern__ = r'https?://(?:www\.)?letsupload\.co/\w+'
    __config__ = [("activated", "bool", "Activated", True),
                  ("use_premium", "bool", "Use premium account if available", True),
                  ("fallback", "bool", "Fallback to free download if premium fails", True),
                  ("chk_filesize", "bool", "Check file size", True),
                  ("max_wait", "int", "Reconnect if waiting time is greater than minutes", 10)]

    __description__ = """Letsupload.co hoster plugin"""
    __license__ = "GPLv3"
    __authors__ = [("gonapo", "nh189[AT]uranus.uni-freiburg[DOT]de"),
                   ("GammaC0de", "nitzo2001[AT]yahoo[DOT]com")]

    WAIT_PATTERN = r'var seconds = (\d+)'

    NAME_PATTERN = r'<i class="fa fa-file-text"></i>(?P<N>.+?)<'
    SIZE_PATTERN = r'<i class="fa fa-hdd-o"></i> size : <p>(?P<S>[\d.,]+) (?P<U>[\w^_]+)</p>'

    OFFLINE_PATTERN = r'>&nbsp;File has been removed\.<'
    LINK_FREE_PATTERN = r"<a class='btn btn-free' href='(.+?)'"

    def setup(self):
        self.multiDL = True

    def check_download(self):
        check = self.scan_download({
            'Html file': re.compile(r'\A\s*<script type=["\']text/javascript["\']')
        })

        if check is not None:
            with open(self.last_download, "r") as f:
                self.data = f.read()

            os.remove(self.last_download)

            m = re.search(r'<a .*href="(.+?\?download_token=\w+)"', self.data)
            if m is not None:
                self.download(m.group(1))

            else:
                self.log_warning(_("Check result: ") + check, _("Waiting 1 minute and retry"))
                self.wait(60, reconnect=True)
                self.restart(check)

        return SimpleHoster.check_download(self)