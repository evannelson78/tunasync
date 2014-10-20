#!/usr/bin/env python2
# -*- coding:utf-8 -*-
import os
import argparse
import json
from datetime import datetime

from tunasync import TUNASync
from tunasync.hook import JobHook


class IndexPageHook(JobHook):

    def __init__(self, parent, dbfile):
        self.parent = parent
        self.dbfile = dbfile

        self.mirrors = {}
        try:
            with open(self.dbfile) as f:
                _mirrors = json.load(f)
                for m in _mirrors:
                    self.mirrors[m["name"]] = m
        except:
            for name, _ in self.parent.mirrors.iteritems():
                self.mirrors[name] = {
                    'name': name,
                    'last_update': '-',
                    'status': 'unknown',
                }

    def before_job(self, *args, **kwargs):
        pass

    def after_job(self, name='unknown', status="unknown", *args, **kwargs):
        print("Updating tunasync.json")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.mirrors[name] = {
            'name': name,
            'last_update': now,
            'status': status
        }
        with open(self.dbfile, 'wb') as f:

            _mirrors = sorted(
                [m for _, m in self.mirrors.items()],
                key=lambda x: x['name']
            )

            json.dump(_mirrors, f)


if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(prog="tunasync")
    parser.add_argument("-c", "--config",
                        default="tunasync.ini", help="config file")
    parser.add_argument("--dbfile",
                        default="tunasync.json",
                        help="mirror status db file")
    parser.add_argument("--pidfile", default="/var/run/tunasync.pid",
                        help="pidfile")

    args = parser.parse_args()

    with open(args.pidfile, 'w') as f:
        f.write("{}".format(os.getpid()))

    tunaSync = TUNASync()
    tunaSync.read_config(args.config)

    index_hook = IndexPageHook(tunaSync, args.dbfile)

    tunaSync.add_hook(index_hook)

    tunaSync.run_jobs()

# vim: ts=4 sw=4 sts=4 expandtab