#!/usr/bin/env python
"""Objects to represent game entities."""

import random, req, string, hashlib

# make sure the tables exist
req.sql.execute('create table if not exists sessions (id, username)')
req.sql.execute('create table if not exists users (username, password)')
req.sql.execute('create table if not exists grid (row, col, formatted, entity_id)')
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
        return bool(self.username())
    
    def login(self, username, raw_password):
        """Attempt to log in given a username and plaintext password. Returns true if successful."""
        
        # hash the raw password immediately
        password = hashlib.sha1(raw_password).hexdigest()
        
        # query the user database
        req.sql.execute('select password from users where username=?',
                        (username,))
        u = req.sql.fetchone()
        
        # if the user is not in the database, register them now
        if not u:
            # add user/pass combo to database
            req.sql.execute('insert into users values (?, ?)',
                            (username, password))
            # set the username and password
            self._set_username(username)
            self._set_password(password)
            return True
        
        # if the user *is* in the database, check against the
        # stored password to see if they can log in
        else:
            stored_password = u[0]
            if password == stored_password:
                self._set_username(username)
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
        
        if not username:
            raise Exception('trying to set password to anonymous!')
        
        req.sql.execute('update users set password=? where username=?',
                        (password, username))
    
    def username(self):
        """Return the username of the client with this id."""
        req.sql.execute('select username from sessions where id=?', (self.id,))
        name = req.sql.fetchone()

        if not name:
            raise Exception('could not find id in table!')
        
        return name[0]
    
    @staticmethod
    def client():
        """Get the client who sent the request."""
        if req.field.has_key('sid'):
            return User(req.field['sid'])
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

    def __init__(self, row, col):
        self.row = row
        self.col = col
        
        # check if this square is in the grid yet,
        # if not, add it
        req.sql.execute('select * from grid where row=? and col=?',
                        (self.row, self.col))
        if not req.sql.fetchone():
            req.sql.execute('insert into grid values (?,?,0,null)',
                            (self.row, self.col))

    
    def __str__(self):
        return '(%s, %s)' % (self.row, self.col)
    
    def has_entity(self):
        """Return if there is an entity at this square."""
        
        return bool(self.get_entity())
    
    def get_entity(self):
        """Return the entity located at this grid square, or None."""
        
        req.sql.execute('select entity_id from grid where row=? and col=?',
                        (self.row, self.col))
        q = req.sql.fetchone()
        if q:
            entity_id = q[0]
            if entity_id:
                return Entity(q[0])
        
    def is_formatted(self):
        """Return true if the square is formatted."""
        
        # get square data from the table
        req.sql.execute('select formatted from grid where row=? and col=?',
                        (self.row, self.col))
        formatted = req.sql.fetchone()
        
        # fail loudly if there is 
        # (it never should)
        if not formatted:
            raise Exception('could not find square in table')
        
        return bool(formatted[0])
    
    def format(self):
        """Set the square's formatted flag to true."""
        
        req.sql.execute('update grid set formatted=1 where row=? and col=?',
                        (self.row, self.col))
        

if __name__ == '__main__':
    print 'TEST RUN'
        
    req.done()
