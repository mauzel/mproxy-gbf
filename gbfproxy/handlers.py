#!/usr/bin/env python
# -*- coding: utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler
import threading
import csv
import os
import gzip
import requests
import StringIO
import logging


F_LIST_LOCK = threading.Lock()
TEMP_SUFFIX = '.temp'
CONTENT_ENC = 'content-encoding'
TRANSFER_ENC = 'transfer-encoding'


def write_file(path, data, url, url_list_path):
    temp_path = path + TEMP_SUFFIX
    if os.path.exists(path) or os.path.exists(temp_path):
        return

    cache_dir = os.path.dirname(path)
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    with open(temp_path, 'wb') as f:
        f.write(data)

    os.rename(temp_path, path)

    logging.debug('Updating cache list: {0}'.format(url_list_path))
    F_LIST_LOCK.acquire()
    with open(url_list_path, 'ab') as csvf:
        w = csv.writer(csvf, quoting=csv.QUOTE_ALL)
        w.writerow([os.path.basename(path), url, len(data)])
    F_LIST_LOCK.release()


def gbf_caching_handler_factory(gbf_conf, executor, uri_matcher,
    headers_matcher):

    class GBFCachingHandler(BaseHTTPRequestHandler, object):
        CACHE_DIR = None
        CACHE_LIST_PATH = None
        EXECUTOR = None
        URI_MATCHER = None
        HEADERS_MATCHER = None

        def __init__(self, *args, **kwargs):
            self.CACHE_DIR = gbf_conf.cache
            self.CACHE_LIST_PATH = os.path.join(gbf_conf.cache, '.cache_list')
            self.EXECUTOR = executor
            self.URI_MATCHER = uri_matcher
            self.HEADERS_MATCHER = headers_matcher
            super(GBFCachingHandler, self).__init__(*args, **kwargs)

        def _fetch_path(self):
            logging.debug('Opening url: {0}'.format(self.path))
            return requests.get(self.path, headers=self.headers)

        def _cache_data(self):
            cache_filename = self.path.split('/')[-1]
            cache_path = os.path.join(self.CACHE_DIR, cache_filename)

            if cache_filename and os.path.exists(cache_path):
                logging.debug('Cache hit: {0} ({1})'.format(self.path,
                    cache_path))
                with open(cache_path, 'rb') as f:
                    data = f.read()
            else:
                logging.debug('Cache miss: {0}'.format(self.path))
                get_resp = self._fetch_path()
                data = get_resp.content
                headers = get_resp.headers

                if cache_filename and self.HEADERS_MATCHER.matches(headers):
                    fut = executor.submit(write_file, cache_path, data,
                        self.path, self.CACHE_LIST_PATH)

            return data

        def do_GET(self):
            if self.URI_MATCHER.matches(self.path):
                data = self._cache_data()
            else:
                data = self._fetch_path().content

            self.send_response(200)
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            self.data = self.rfile.read(int(self.headers['Content-Length']))

            response = requests.post(self.path, headers=self.headers,
                data=self.data)
            self.handle_response(response)

        def handle_response(self, response):
            if response.status_code < 400:
                self.send_response(response.status_code)
            else:
                self.send_error(response.status_code)

            for k, v in response.headers.items():
                self.send_header(k, v)
            self.end_headers()

            output = response.content
            headers = response.headers

            # gzip
            if CONTENT_ENC in headers and \
                    headers[CONTENT_ENC].lower() == 'gzip':
                buffer = StringIO.StringIO()
                with gzip.GzipFile(fileobj=buffer, mode='w') as f:
                    f.write(output)
                output = buffer.getvalue()

            # chunking
            if TRANSFER_ENC in headers and \
                    headers[TRANSFER_ENC].lower() == 'chunked':
                self.wfile.write('{0}\r\n%s{1}\r\n'.format(len(output),
                    output))
                self.wfile.write('0\r\n\r\n')
            else:
                self.wfile.write(output)

    return GBFCachingHandler