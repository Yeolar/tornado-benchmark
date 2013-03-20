tornado-benchmark
=================

A benchmark and URL checking tool based on tornado.

Usage:

1. benchmark:

    $ torbench http://localhost/ ...    # console output
    $ torbench --use_curl --max_clients=10 --multi_processes=100 --time_len=300 --timeout=5.0 --urls_file=bench_urls.conf --log_file_prefix=bench1000.log
    $ toranalyer --max_clients=10 --multi_processes=100 bench1000.log

2. URL checker:

    $ torchecker check_urls.conf

--help for more details, and an instruction is available at: http://www.yeolar.com/note/2013/03/16/tornado-benchmark/ .

If any questions, please contact Yeolar <yeolar@gmail.com>.
