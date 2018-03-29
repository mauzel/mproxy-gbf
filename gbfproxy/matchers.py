#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from urllib.parse import urlparse
import hashlib
import logging


class GBFUriMatcher:
    def __init__(self, regex):
        logging.debug('Using {0}'.format(regex))
        self.pattern = re.compile(regex)

    def matches(self, uri):
        return bool(self.pattern.match(uri))


class GBFHeadersMatcher:
    def matches(self, headers):
        content_type = headers['Content-Type'].lower()
        return 'image' in content_type or 'audio' in content_type


class GBFCacheNamer:
    def to_cache_name(self, url):
        p = urlparse(url)
        return hashlib.sha1((p.path).encode('utf-8')).hexdigest()
