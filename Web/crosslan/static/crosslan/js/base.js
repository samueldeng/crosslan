/*******************************jQuery Plugin************************************/
// Get Parameters From Query String
// Usage:
//		$.QueryString["paraname"]
(function($) {
    $.QueryString = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
})(jQuery);
// End
/****************************jQuery Plugin End***********************************/

$(document).ready(function(){
	$('li#userDrop').mouseenter(function(){
		$(this).children('a').click();
	}).mouseout(function(){
	});
});
