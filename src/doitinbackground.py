#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of PushBullet-Commons
#
# Copyright (C) 2014-2016
# Lorenzo Carbonell Cerezo <lorenzo.carbonell.cerezo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from threading import Thread
from idleobject import IdleObject
from gi.repository import GObject
import requests
import glob
import os
from urllib.parse import unquote_plus
from os.path import basename


def download_file(url, filename):
    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS \
X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 \
Safari/537.36'
    }
    try:
        r = requests.get(url, stream=True, headers=headers)
        print('----', url, filename, '----')
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return True
    except Exception as e:
        print(e)
    return False


class DoitInBackground(Thread, IdleObject):
    __gsignals__ = {
        'started': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'started_one': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'finished_one': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'stopit': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, urls, folder):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.daemon = True
        self.urls = urls
        self.folder = folder
        self.stop = False

    def stopit(self):
        self.stop = True

    def run(self):
        self.emit('started')
        for url in self.urls:
            if self.stop is True:
                self.emit('stopit')
                return
            filename = unquote_plus(unquote_plus(unquote_plus(basename(url))))
            filepath = os.path.join(self.folder, filename)
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filepath)
                nfiles = len(glob.glob(base+'*'+ext))
                filepath = base+'_'+str(nfiles)+ext
            self.emit('started_one', filepath)
            print('----', url, filepath, '----')
            download_file(url, filepath)
            self.emit('finished_one', filepath)
        self.emit('finished')
