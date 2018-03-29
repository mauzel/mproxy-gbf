#!/usr/bin/env python
# -*- coding: utf-8 -*-
from http.server import HTTPServer
from socketserver import ThreadingMixIn
import socket
import logging


SUPPORTED_PROTOCOLS = [
    'HTTP/1.1'
]


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True


class GBFProxyServer:
    def __init__(self, gbf_conf, handler_cls, server_cls=ThreadedHTTPServer):
        self.host = gbf_conf.host
        self.port = gbf_conf.port
        self.protocol = gbf_conf.protocol.upper()

        assert self.protocol in SUPPORTED_PROTOCOLS, 'Got unsupported ' \
            'protocol: {0}. Supported protocols: {1}'.format(
            protocol, SUPPORTED_PROTOCOLS)

        listen_on = (self.host, self.port)
        self.server = server_cls(listen_on, handler_cls)

    def run(self):
        sock_addr = self.server.socket.getsockname()
        logging.info('Starting proxy on {0}:{1}'.format(sock_addr[0],
            sock_addr[1]))
        self.server.serve_forever()
