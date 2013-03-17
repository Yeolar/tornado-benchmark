tornado-benchmark
=================

A benchmark tool based on tornado.

Usage:

    $ ./benchclient.py http://localhost/ ...    # console output
    $ ./benchclient.py --use_curl --max_clients=10 --multi_processes=100 --time_len=300 --timeout=5.0 --urls_file=urls.conf --log_file_prefix=bench1000.log
    $ ./analyzer.py --max_clients=10 --multi_processes=100 bench1000.log

--help for more details, and an instruction is available at: http://www.yeolar.com/note/2013/03/16/tornado-benchmark/ .

If any questions, please contact Yeolar <yeolar@gmail.com>.
