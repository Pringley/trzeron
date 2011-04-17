#!/usr/bin/env python
# Copyright (c) 2011, Ben Pringle
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Framework code to respond to XMLHttpRequests.

Important variables:
field -- the cgi.FieldStorage object containing POST data
ip -- the IP address from which the request originates
sql -- the SQLlite cursor
out -- a dictionary to be returned in JSON

"""

import sys, os, cgi, json, sqlite3, Cookie

# print header
print 'Content-Type: text/plain'
print

# uncomment to enable error output in browser
sys.stderr = sys.stdout

# set up CGI (input data)
field = cgi.FieldStorage()
ip = os.getenv('HTTP_CLIENT_IP') or os.getenv('HTTP_X_FORWARDED_FOR') or os.getenv('REMOTE_ADDR') or 'UNKNOWN'

# set up SQL (store data)
sqlite_connection = sqlite3.connect('sql.db')
sql = sqlite_connection.cursor()
nonalpha = ''.join(c for c in map(chr, range(256)) if not c.isalnum())
def sanitize(input_string):
    '''Given a string, strip all non-alphanumeric characters.'''
    return input_string.translate(None, nonalpha)

# set up JSON (output data)
out = {}

def done():
    """Close the connection to SQLite and print the JSON document."""
    
    # close SQL
    sqlite_connection.commit()
    sql.close()

    # print JSON
    print json.dumps(out, separators=(',',':'))

if __name__ == '__main__':
    done()
