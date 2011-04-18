var _sid = null;
var _logged_in = false;

function logged_in() {
    return _logged_in;
}

function login(username, password) {
    var valid;
    var param = {
	username: username,
	password: password
    };
    if(_sid != null) {
	param.sid = _sid;
    }
    $.ajax({
	type: 'POST',
	url: 'server/xhr.py',
	data: param,
	dataType: 'json',
	async: false,
	timeout: 10000,
	error: function() {
	    alert('Timed out!');
	    valid = false;
	},
	success: function(data) {
	          var items = [];
		  
		  $.each(data, function(key, val) {
		      if(key == 'sid') {
			  _sid = val;
		      }
		      if(key == 'auth') {
			  valid = val;
		      }
		  });
	}
    });
    if(valid) { _logged_in = true; }
    return valid;
	  
}