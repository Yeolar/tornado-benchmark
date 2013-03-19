#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 2013-03-12.  Copyright (C) Yeolar <yeolar@gmail.com>
#

import sys
import time
import random
import logging

from tornado import ioloop
from tornado import httpclient
from tornado import process

# use a modified options based on tornado's options
from options import define, options, parse_command_line, parse_config_file


define('use_curl', type=bool, default=False, help='use pycurl as AsyncHTTPClient backend')
define('multi_processes', type=int, default=-1, help='run as multi-processes, 0 for cpu count')
define('max_clients', type=int, default=10, help='max concurrent clients')
define('time_len', type=int, default=60, help='time length of the test')
define('timeout', type=float, default=1.0, help='request timeout')
define('follow_redirects', type=bool, default=True, help='request follow redirects')
define('validate_cert', type=bool, default=True, help='request validate cert')
define('urls_file', help='request urls file')
define('url_template', help='request url template, if not "", build with values in urls_file')
define('log_info_format', help='info log format')
define('log_warning_format', help='warning log format')
define('log_error_format', help='error log format')

requests = parse_command_line()
parse_config_file('settings.py')

if options.use_curl:
    httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')
else:
    httpclient.AsyncHTTPClient.configure(
            'simple_httpclient.SimpleAsyncHTTPClient')


class BenchClient(object):

    def __init__(self, requests, timeout, max_clients, time_len=60):
        assert requests

        self._io_loop = ioloop.IOLoop()
        self._client = httpclient.AsyncHTTPClient(
                self._io_loop, max_clients=max_clients)

        self.requests = requests
        self.timeout = timeout
        self.max_clients = max_clients
        self.time_len = time_len

    def get_request(self):
        request = random.choice(self.requests)
        if not isinstance(request, httpclient.HTTPRequest):
            request = httpclient.HTTPRequest(request,
                    follow_redirects=options.follow_redirects,
                    validate_cert=options.validate_cert,
                    request_timeout=self.timeout)
        return request

    def bench(self):
        for i in xrange(self.max_clients):
            self._client.fetch(self.get_request(), self._on_response)

        self.start = time.time()
        self.end = self.start + self.time_len

        self._io_loop.start()

    def _on_response(self, response):
        if time.time() > self.end:
            if options.use_curl:
                self._client.close()
            self._io_loop.stop()
            return

        self.log(response)

        self._client.fetch(self.get_request(), self._on_response)

    def log(self, response, k=0):
        if response.error:
            logging.warning(options.log_warning_format,
                    response.request_time,
                    response.code,
                    response.request.url,
                    response.error)
        else:
            logging.info(options.log_info_format,
                    response.request_time,
                    response.code,
                    response.request.url)


def main():
    if options.urls_file:
        with open(options.urls_file) as f:
            lines = [line for line in f.read().splitlines()
                    if not line.startswith('#')]
            if options.url_template:
                lines = [options.url_template % line for line in lines]
            requests.extend(lines)
    if not requests:
        sys.exit(0)

    if options.multi_processes != -1:
        process.fork_processes(options.multi_processes)

    bc = BenchClient(requests, options.timeout, options.max_clients,
            options.time_len)
    bc.bench()


if __name__ == '__main__':
    main()
