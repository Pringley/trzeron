var _sid = null; // global session id

/**
 * Check with the server if the user is authenticated.
 *
 * callback - function to be called when the server replies;
 *            takes a boolean argument that is true if the
 *            user is logged in
 */
function logged_in(callback) {
    _query(
	{},
	function(data) {
	    callback(data.auth);
    });
}

/**
 * Attempt to log in to the server.
 *
 * username - alphanumeric username (strings with symbols will
 *            be rejected by the server)
 * password - plaintext password string
 * callback - function to be called when the server replies;
 *            takes a boolean argument that is true if the
 *            login is successful (or the user was previously
 *            logged in)
 *
 * If the username has not yet been used, the server will accept
 * the login and store the given password. Then, in order to
 * re-use that username successfully, one has to supply that
 * password again.
 */

function login(username, password, callback) {
    _query(
	{
	    username:username,
	    password:password
	},
	function(data) {
	    callback(data.auth);
	}
    );
    
}
/*
 * Make a query to the server using AJAX.
 *
 * param    - set of POST inputs
 * callback - function to be called when the server request;
 *            takes an argument containing the server's reply
 */
function _query(param, callback) {
    if(_sid != null) {
	// send the session id to the server if we have one
	param.sid = _sid;
    }
    return $.post('server/xhr.py', param, 'json')
	.success(function(data) {
	    // synchronize the sesion id with the server
	    _sid = data.sid;
	    callback(data);
	})
	.error(function() {
	    alert('Error fetching data from server.');
	});
}