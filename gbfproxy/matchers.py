#!/usr/bin/env python
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import threading
import csv
import os
import gzip
import requests
import io
import logging


F_LIST_LOCK = threading.Lock()
TEMP_SUFFIX = '.temp'
CONTENT_ENC = 'content-encoding'
TRANSFER_ENC = 'transfer-encoding'
CONTENT_LEN = 'content-length'
ACCESS_CONTROL_ALLOW = 'access-control-allow-origin'


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

    if os.path.getsize(temp_path) == 0:
        logging.debug('Got zero byte cache file: {0}'.format(url))
        return

    os.rename(temp_path, path)

    if os.stat(path).st_size == 0:
        logging.error('Bad file size: {0}'.format(path))
        os.remove(path)

    logging.debug('Updating cache list: {0}'.format(url_list_path))
    F_LIST_LOCK.acquire()
    with open(url_list_path, 'a') as csvf:
        w = csv.writer(csvf, quoting=csv.QUOTE_ALL)
        w.writerow([os.path.basename(path), url, len(data)])
    F_LIST_LOCK.release()


def gbf_caching_handler_factory(gbf_conf, executor, uri_matcher,
    headers_matcher, cache_namer):

    class GBFCachingHandler(BaseHTTPRequestHandler):
        CACHE_DIR = None
        CACHE_LIST_PATH = None
        CACHE_NAMER = None
        EXECUTOR = None
        URI_MATCHER = None
        HEADERS_MATCHER = None

        def __init__(self, *args, **kwargs):
            self.CACHE_DIR = gbf_conf.cache
            self.CACHE_LIST_PATH = os.path.join(gbf_conf.cache, '.cache_list')
            self.EXECUTOR = executor
            self.URI_MATCHER = uri_matcher
            self.HEADERS_MATCHER = headers_matcher
            self.CACHE_NAMER = cache_namer
            super(GBFCachingHandler, self).__init__(*args, **kwargs)

        def _fetch_path(self):
            return requests.get(self.path, headers=self.headers)

        def _cache_data(self):
            cache_filename = self.CACHE_NAMER.to_cache_name(self.path)
            cache_path = os.path.join(self.CACHE_DIR, cache_filename)
            response = None

            if cache_filename and os.path.exists(cache_path):
                logging.debug('Cache hit: {0} ({1})'.format(self.path,
                    cache_path))
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    response = requests.Response()
                    setattr(response, 'status_code', 200)
                    setattr(response, '_content', data)
                    setattr(response, 'headers', {
                        CONTENT_LEN: str(len(data)),
                        CONTENT_ENC: 'identity',
                        ACCESS_CONTROL_ALLOW: '*'

                    })
            else:
                response = self._fetch_path()
                data = response.content
                headers = response.headers

                if cache_filename and self.HEADERS_MATCHER.matches(headers):
                    logging.debug('Cache miss: {0}'.format(self.path))
                    fut = executor.submit(write_file, cache_path, data,
                        self.path, self.CACHE_LIST_PATH)

            return response

        def do_GET(self):
            if self.URI_MATCHER.matches(self.path):
                response = self._cache_data()
            else:
                response = self._fetch_path()

            self.handle_response(response)

        def do_POST(self):
            self.data = self.rfile.read(int(self.headers['Content-Length']))

            response = requests.post(self.path, headers=self.headers, data=self.data)

            self.handle_response(response)

        def do_DELETE(self):
            self.data = self.rfile.read(int(self.headers['Content-Length']))

        def handle_response(self, response):
            if response.status_code < 400:
                self.send_response(response.status_code)
            else:
                self.send_error(response.status_code)

            output = response.content
            headers = response.headers

            # requests already decompressed gzip
            if CONTENT_ENC in headers and \
                    headers[CONTENT_ENC].lower() == 'gzip':
                headers[CONTENT_ENC] = 'identity'
                headers[CONTENT_LEN] = str(len(output))

            for k, v in headers.items():
                self.send_header(k, v)

            self.end_headers()
            self.wfile.write(output)

        def log_message(self, fmt, *args):
            pass

    return GBFCachingHandler
