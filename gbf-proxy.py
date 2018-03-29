#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gbfproxy.proxy import GBFProxyServer
from gbfproxy.configparser import GBFConfigParser
from gbfproxy.matchers import GBFUriMatcher, GBFHeadersMatcher, GBFCacheNamer
from gbfproxy.handlers import gbf_caching_handler_factory
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.handlers
import coloredlogs
import os
import argparse


LOG_FMT = ('%(asctime)s.%(msecs)03d '
           '[(%(threadName)s) %(filename)s %(funcName)s %(lineno)d] '
           '%(levelname)s: %(message)s')
GBF_INI_FILENAME = 'gbf-proxy.ini'
GBF_LOG_FILE = os.path.join('logs', 'gbf-proxy.log')


PARSER = argparse.ArgumentParser(description='granblue fantasy caching proxy')
PARSER.add_argument('-c', '--config', default=GBF_INI_FILENAME,
                    help='path to an INI file (default: {0})'.format(
                        GBF_INI_FILENAME))
PARSER.add_argument('-d', '--debug', action='store_true',
                    help='set logging level to debug mode')
PARSER.add_argument('-l', '--logfile', default=GBF_LOG_FILE,
                    help='set logfile (default: {0})'.format(
                        GBF_LOG_FILE))
PARSER.add_argument('--console-output', action='store_true',
                    help='output logs to console instead of to file')


def configure_logging(args, fmt):
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    if args.console_output:
        coloredlogs.install(fmt=fmt, level=log_level)
    else:
        # Create logfile if it doesn't exist
        log_dir = os.path.dirname(args.logfile)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        handler = logging.handlers.TimedRotatingFileHandler(
            args.logfile, when='midnight', backupCount=7)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(log_level)


def main():
    args = PARSER.parse_args()
    configure_logging(args, LOG_FMT)

    # Instiate all the stuff needed for the proxy handler
    gbf_conf = GBFConfigParser().parse(os.path.abspath(args.config))
    logging.debug('GBF conf: {0}'.format(gbf_conf))
    uri_matcher = GBFUriMatcher(gbf_conf.matcher)
    headers_matcher = GBFHeadersMatcher()
    cache_namer = GBFCacheNamer()
    executor = ThreadPoolExecutor(5)
    handler_cls = gbf_caching_handler_factory(gbf_conf, executor, uri_matcher,
        headers_matcher, cache_namer)

    proxy_server = GBFProxyServer(gbf_conf, handler_cls=handler_cls)

    while True:
        try:
            proxy_server.run()
        except:
            logging.exception('Got error while running')


if __name__ == '__main__':
    main()
