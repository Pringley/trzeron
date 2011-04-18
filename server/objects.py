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
"""Objects to represent game entities."""

import random, req, string, hashlib

# make sure the tables exist
req.sql.execute('create table if not exists sessions (id, username)')
req.sql.execute('create table if not exists users (username, password, entity_id)')
req.sql.execute('create table if not exists grid (row, col, data_type, entity_id, owner)')
req.sql.execute('create table if not exists entities (id)')

def new_id(table):
    """Generate a random base64 id that's not already in the entity table."""
    
    id = ''.join([random.choice(string.ascii_letters + string.digits + '+-') for i in range(10)])
    
    # check if the generated id is already in use,
    # if so, recursively generate a new one
    req.sql.execute('select * from %s where id="%s"' % (table, id))
    if req.sql.fetchone():
        id = new_id()
    
    return id
    

class User:
    """A client playing the game."""
    
    def __init__(self, id):
        self.id = id
    
    def is_logged_in(self):
        """Return true if the user is authenticated."""
        return self.username() is not None
    
    def login(self, username, raw_password):
        """Attempt to log in given a username and plaintext password.
        
        The username and password are not assumed to be safe for verbatim
        insertion into the database. The username must be alphanumeric
        (otherwise the login will fail). The password is hashed using SHA1
        before being inserted into the database.

        Returns true if successful.
        
        """
        
        # protect against SQL injection
        clean_username = req.sanitize(username)
        
        # 
        if not clean_username == username:
            req.error('bad username')
            return False
        
        # hash the raw password
        password = hashlib.sha1(raw_password).hexdigest()
        
        # query the user database
        req.sql.execute('select password from users where username=?',
                        (clean_username,))
        u = req.sql.fetchone()
        
        # if the user is not in the database, register them now
        if not u:
            # add user/pass combo to database
            req.sql.execute('insert into users values (?, ?, null)',
                            (clean_username, password))
            # set the username and password
            self._set_username(clean_username)
            self._set_password(password)
            return True
        
        # if the user *is* in the database, check against the
        # stored password to see if they can log in
        else:
            stored_password = u[0]
            if password == stored_password:
                self._set_username(clean_username)
                return True
            else:
                return False
    
    def _set_username(self, username):
        """(internal) Set the username of the client."""
               
        # clear old sessions of this user
        req.sql.execute('delete from sessions where username = ?',
                        (username,))
        
        # set this session's username in the database
        req.sql.execute('update sessions set username=? where id=?',
                       (username, self.id))
            
    def _set_password(self, password):
        """(internal) Set the password of the user."""
        
        username = self.username()
        
        # this is an internal method and shouldn't be called
        # unless the username is already set -- if for some
        # reason it is, fail loudly
        if username is None:
            raise Exception('trying to set password to anonymous!')
        
        req.sql.execute('update users set password=? where username=?',
                        (password, username))
    
    def username(self):
        """Return the username of the client with this id."""
        
        # query the database
        req.sql.execute('select username from sessions where id=?', (self.id,))
        q = req.sql.fetchone()
        if q and q[0]:
            return q[0]
    
    @staticmethod
    def client():
        """Get the client who sent the request."""
        if req.field.has_key('sid'):
            return User(req.field['sid'].value)
        else:
            id = new_id('sessions')
            req.sql.execute('insert into sessions values (?, null)', (id,))
            return User(id)

class Entity:
    """A game entity."""
    
    def __init__(self, id=None):
        if not id:
            # create a new entity (add to table)
            id = new_id('entities')
            req.sql.execute('insert into entities values (?)',(id,))
        
        self.id = id
        
    
    def set_square(self, square):
        """Move the entity to a square on the grid."""
        
        # remove entity from current square
        req.sql.execute('update grid set entity_id=null where entity_id=?',
                        (self.id,))
        
        # place entity in new square
        req.sql.execute('update grid set entity_id=? where row=? and col=?',
                        (self.id, square.row, square.col))
    
    def get_square(self):
        """Find the square at which the entity is located."""
        req.sql.execute('select row, col from grid where entity_id=?', (self.id,))
        
        q = req.sql.fetchone()
        if q:
            return Square(q[0], q[1])
        
    def delete(self):
        """Remove the entity from the database."""
        req.sql.execute('delete from entities where id=?',(self.id,))

class Square:
    """A square on the grid."""
    
    # dictionary containing the map from integer to square type
    DATA_VALUES = {

        0: 'unformatted',     # unowned grid space; must be formatted
                              # before it's of any use

        1: 'base',            # a player's main base; can only have
                              # one per player

        2: 'memory',          # grid space owned by a player

    }
    
    def __init__(self, row, col):
        self.row = row
        self.col = col
        
        # check if this square is in the grid yet,
        # if not, add it
        req.sql.execute('select * from grid where row=? and col=?',
                        (self.row, self.col))
        if not req.sql.fetchone():
            req.sql.execute('insert into grid values (?,?,0,null,null)',
                            (self.row, self.col))

    
    def __str__(self):
        # just print the (row, col) pair
        return '(%s, %s)' % (self.row, self.col)
    
    def get_owner(self):
        """Return the username of the player who owns this square."""
        
        req.sql.execute('select owner from grid where row=? and col=?',
                        (self.row, self.col))
        q = req.sql.fetchone()
        
        # fail loudly if there isn't data 
        # (there should always be data)
        if not q:
            raise Exception('could not find square in table')
        
        owner_name = q[0]
        return owner_name
    
    def has_owner(self):
        """Return true if a player owns this square."""
        
        return owner_name is not None
    
    def set_owner(self, owner_name):
        """Set the owner of the square."""
        
        req.sql.execute('update grid set owner=? where row=? and col=?',
                        (owner_name, self.row, self.col))
    
    def has_entity(self):
        """Return true if there is an entity at this square."""
        
        return self.get_entity() is not None
    
    def get_entity(self):
        """Return the entity located at this grid square, or None."""
        
        # query the database
        req.sql.execute('select entity_id from grid where row=? and col=?',
                        (self.row, self.col))
        q = req.sql.fetchone()
        
        # fail loudly if there isn't data 
        # (there should always be data)
        if not q:
            raise Exception('could not find square in table')
        
        entity_id = q[0]
            
        # if there exists an id in the table,
        # return its corresponding entity
        if entity_id is not None:
            return Entity(q[0])
    
    def set_entity(self, entity):
        """Set the entity's location to this square.
        
        If the entity was previously located at another square, it
        will be moved to this one.
        
        """
        
        # just use the Entity object's move method
        entity.set_square(self)
        
    def get_data_type(self):
        """Return an integer representing the data type of the square."""
        
        # get square data from the table
        req.sql.execute('select data_type from grid where row=? and col=?',
                        (self.row, self.col))
        q = req.sql.fetchone()
        
        # fail loudly if there isn't data 
        # (there should always be data)
        if not q:
            raise Exception('could not find square in table')
        
        return q[0]
    
    def set_data_type(self, data_type):
        """Set the data type of the square."""
        
        req.sql.execute('update grid set data_type=? where row=? and col=?',
                        (data_type, self.row, self.col))
        

if __name__ == '__main__':
    print 'TEST RUN'
    

    req.done()
