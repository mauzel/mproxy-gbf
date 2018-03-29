#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import configparser
import os


class GBFProxyConfig:
    """Represents configuration values used throughout this program."""

    def __init__(self):
        self.host = None
        self.port = None
        self.protocol = None
        self.cache = None
        self.matcher = None

    def __repr__(self):
        return str(vars(self))


class GBFINIOpts:
    """Represents the keys for configuration options in INI files."""
    HOST = 'host'
    PORT = 'port'
    PROTO = 'protocol'
    CACHE = 'cache'
    MATCHER = 'matcher'


class GBFConfigParser:
    INI_GBFPROXY_SEC = 'GBFPROXY'

    def parse(self, path):
        """Parse a ``GBFProxyConfig`` from an INI file.

        Notes:
            Currently only supports INI configuration files.

        Args:
            path (str): A path to an gbf-proxy configuration file.
        """
        return self._parse_ini(path)

    def _parse_ini(self, path):
        config = configparser.SafeConfigParser()

        logging.debug('attempting to parse ini from {0}'.format(path))
        config.read(path)

        if not config.has_section(self.INI_GBFPROXY_SEC):
            raise KeyError(
                'missing required section: {0}'.format(self.INI_GBFPROXY_SEC))

        gbf_conf = GBFProxyConfig()
        gbf_conf.host = config.get(self.INI_GBFPROXY_SEC, GBFINIOpts.HOST)
        gbf_conf.port = int(config.get(self.INI_GBFPROXY_SEC, GBFINIOpts.PORT))
        gbf_conf.protocol = config.get(self.INI_GBFPROXY_SEC, GBFINIOpts.PROTO)
        gbf_conf.cache = os.path.abspath(config.get(self.INI_GBFPROXY_SEC,
            GBFINIOpts.CACHE))
        gbf_conf.matcher = config.get(self.INI_GBFPROXY_SEC,
            GBFINIOpts.MATCHER)

        return gbf_conf
