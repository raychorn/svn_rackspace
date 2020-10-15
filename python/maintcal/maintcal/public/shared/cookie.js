/*extern Ext, Rack */

/*

Cookie functions from PPK
http://www.quirksmode.org/js/cookies.html

*/
Ext.namespace('Rack');

Rack.createCookie = function (name, value, expires, path, encode) {
    
    if (expires) {
        if (expires instanceof Date) {
            expires = "; expires=" + expires.toGMTString();
        }
        else {
            var date = new Date();
            date.setTime(date.getTime() + (expires * 24 * 60 * 60 * 1000));
	    expires = "; expires=" + date.toGMTString();
        }
    }
    else {
        expires = "";
    }

    if (!path) {
        path = "/";
    }
    if (encode) {
        value = encodeURIComponent(value);
    }
    
    document.cookie = name + "=" + value + expires + "; path=" + path;
};

Rack.readCookie = function (name, encoded) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    var c = null;
    
    for (var i = 0; i < ca.length; i++) {
        if (encoded) {
            c = decodeURIComponent(ca[i]);
        }
        else {
            c = ca[i];
        }
	while (c.charAt(0) === ' ') {
            c = c.substring(1, c.length);
        }
	if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
};

Rack.eraseCookie = function (name) {
    Rack.createCookie(name, "" , -1);
};
