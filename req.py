#!/usr/bin/env python
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
