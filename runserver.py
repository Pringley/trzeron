#!/usr/bin/env python
"""Super light-weight server for testing purposes."""


import BaseHTTPServer, CGIHTTPServer

cgihandler = CGIHTTPServer.CGIHTTPRequestHandler
cgihandler.cgi_directories = ['/']

httpd = BaseHTTPServer.HTTPServer(('',8000), cgihandler)

print 'Server started.'
httpd.serve_forever()
