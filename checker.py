#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 2013-03-18.  Copyright (C) Yeolar <yeolar@gmail.com>
#

import sys
import time
import random
import logging

from tornado import ioloop
from tornado import httpclient
from tornado import process
from tornado.options import (define, options,
        parse_command_line, parse_config_file)


define('use_curl', type=bool, default=False, help='use pycurl as AsyncHTTPClient backend')
define('max_clients', type=int, default=10, help='max concurrent clients')
define('timeout', type=float, default=5.0, help='request timeout')
define('retry_times', type=int, default=3, help='retry times')
define('follow_redirects', type=bool, default=True, help='request follow redirects')
define('validate_cert', type=bool, default=True, help='request validate cert')
define('checker_log_format', help='log format')

urls_files = parse_command_line()
parse_config_file('settings.py')

if options.use_curl:
    httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')
else:
    httpclient.AsyncHTTPClient.configure(
            'simple_httpclient.SimpleAsyncHTTPClient')


class Entry(object):

    def __init__(self, url, code, keyword, retry_times):
        self.url = url
        self.code = code
        self.keyword = keyword
        self.retry_times = retry_times
        self.retry_no = 1
        self.error = ''

    def check_response(self, response):
        if response.error:
            self.error = 'error:[%s]' % response.error
            return

        self.error = ''
        if self.code != response.code:
            self.error = 'error:[unmatch code:%d' % response.code
        if self.keyword and self.keyword not in response.body:
            if self.error:
                self.error += ', keyword not found'
            else:
                self.error = 'error:[keyword not found'
        if self.error:
            self.error += ']'

    @staticmethod
    def make(s, retry_times):
        l = s.split('|')
        url = l[0]
        code = int(l[1]) if len(l) > 1 else 200
        keyword = l[2] if len(l) > 2 else ''
        retry_times = int(l[3]) if len(l) > 3 else retry_times
        return Entry(url, int(code), keyword, retry_times)


class Checker(object):

    def __init__(self, entries, timeout, max_clients):
        assert entries

        self._io_loop = ioloop.IOLoop()
        self._client = httpclient.AsyncHTTPClient(
                self._io_loop, max_clients=max_clients)

        self.timeout = timeout
        self.max_clients = max_clients
        self.requests = dict([(self.get_request(e), e) for e in entries])
        self.count = len(self.requests)

    def get_request(self, entry):
        return httpclient.HTTPRequest(entry.url,
                follow_redirects=options.follow_redirects,
                validate_cert=options.validate_cert,
                request_timeout=self.timeout)

    def check(self):
        for request in self.requests:
            self._client.fetch(request, self._on_response)

        self._io_loop.start()

    def _on_response(self, response):
        self.count -= 1

        request = response.request
        entry = self.requests[request]
        entry.check_response(response)

        if entry.error:
            if entry.retry_no < entry.retry_times:
                self.log('warning', entry, response)
                self.requests[request].retry_no += 1
                self.count += 1
                self._client.fetch(request, self._on_response)
            else:
                self.log('error', entry, response)
        else:
            self.log('info', entry, response)

        if self.count == 0:
            if options.use_curl:
                self._client.close()
            self._io_loop.stop()

    def log(self, level, entry, response):
        getattr(logging, level)(options.checker_log_format,
                response.request_time,
                entry.url,
                entry.code,
                entry.keyword,
                entry.retry_no,
                entry.retry_times,
                entry.error)


def main():
    entries = []
    for urls_file in urls_files:
        with open(urls_file) as f:
            for line in f.read().splitlines():
                if not line.startswith('#'):
                    entries.append(Entry.make(line, options.retry_times))
    if not entries:
        sys.exit(0)

    bc = Checker(entries, options.timeout, options.max_clients)
    bc.check()


if __name__ == '__main__':
    main()
