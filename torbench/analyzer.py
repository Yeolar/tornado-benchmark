#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 2013-03-14.  Copyright (C) Yeolar <yeolar@gmail.com>
#

import os
import sys
import re
from datetime import datetime, timedelta
import logging

from tornado import process
try:
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    rcParams['savefig.dpi'] = options.dpi
except ImportError:
    plt = None

from utils import setup_settings
from options import define, options, parse_command_line, parse_config_file


define('multi_processes', type=int, default=-1, help='benched as multi-processes')
define('max_clients', type=int, default=10, help='max concurrent clients')
define('dpi', type=int, default=72, help='figure DPI')
define('figure_file', default='log.png', help='figure file')

parse_config_file(setup_settings())
log_files = parse_command_line()


REGEX = re.compile(r'\[(?P<level>[IWE]) (?P<date>\d+) (?P<time>[\d:\.]+)'
                   r' (?P<file>\w+):(?P<lineno>\d+)\]'
                   r' cost:\[(?P<cost>[\d\.]+)\]'
                   r' code:\[(?P<code>\d+)\]'
                   r' url:\[(?P<url>\S+)\]'
                   r'( error:\[(?P<error>[^\]]+)\])?')

LEVEL_MAP = {
    'I': 'info',
    'W': 'warning',
    'E': 'error',
}


class LogEntry(object):

    def __init__(self, level, dtime, cost, url, error=None):
        self.level = level
        self.dtime = dtime
        self.cost = cost
        self.url = url
        self.error = error

    @staticmethod
    def make(log_str):
        m = REGEX.match(log_str)
        if not m:
            logging.debug('Can not parse: %s', log_str)
            return None

        dt_str = m.group('date') + m.group('time')
        return LogEntry(
                LEVEL_MAP[m.group('level')],
                datetime.strptime(dt_str, '%y%m%d%H:%M:%S.%f'),
                float(m.group('cost')),
                m.group('url'),
                m.group('error'))


class LogAnalyzer(object):

    def __init__(self, concurrency, process_num):
        self.concurrency = concurrency
        self.process_num = process_num

        self._entries = []
        self.normal_requests = []
        self.error_requests = []
        self.time_len = 0

    def append(self, log_entry):
        if log_entry:
            self._entries.append(log_entry)

    def run(self):
        for entry in self._entries:
            if entry.error:
                self.error_requests.append((entry.dtime, entry.cost))
            else:
                self.normal_requests.append((entry.dtime, entry.cost))

        starts = [e.dtime - timedelta(seconds=e.cost) for e in self._entries]
        ends = [e.dtime for e in self._entries]
        time_len = max(ends) - min(starts)
        self.time_len = time_len.seconds + time_len.microseconds / 1000000.0

    def print_stat(self):
        assert self._entries

        lt = len(self._entries)
        ln = len(self.normal_requests)
        le = len(self.error_requests)
        average_cost = sum([e.cost for e in self._entries]) / lt

        print 'Tornado Bench Client'
        print
        print 'Concurrency level:       %d' % self.concurrency
        print 'Process number:          %d' % self.process_num
        print 'Time length for tests:   %d sec' % self.time_len
        print 'Requests:                %d/%d (%f)' % ( ln, lt, float(ln) / lt)
        print 'Requests per second:     %.2f /sec (mean)' % (float(lt) / self.time_len)
        print 'Time per requests:       %.6f sec (mean, across all concurrent requests)' % (self.time_len / float(lt))
        print 'Request cost:            %.6f sec (mean)' % average_cost

    def draw_figure(self, file_name):
        x, y = zip(*self.normal_requests)
        plt.plot(x, y, '.', markersize=2)
        x, y = zip(*self.error_requests)
        plt.plot(x, y, 'r.', markersize=2)
        plt.legend(('Normal request', 'Error request'), 'upper right')
        plt.xlabel('Time')
        plt.ylabel('Cost')
        plt.savefig(file_name, format=os.path.splitext(file_name)[1][1:])


def main():
    if not len(log_files):
        print 'please specified log files.'
        sys.exit(0)

    process_num = {
        -1: 1,
        0: process.cpu_count(),
    }.get(options.multi_processes, options.multi_processes)

    la = LogAnalyzer(options.max_clients, process_num)

    for log_file in log_files:
        with open(log_file) as f:
            for line in f.read().splitlines():
                la.append(LogEntry.make(line))

    la.run()
    la.print_stat()
    if plt:
        la.draw_figure(options.figure_file)


if __name__ == '__main__':
    main()
