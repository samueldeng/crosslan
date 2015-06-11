$(document).ready(function(){
	$('#inputUsername').focus();

	$('#formSignin').submit(function(e){
		// var pass = $("#inputPassword").prop("value");
		// if(pass == "" || pass == $("#inputPassword").attr("value")){
		// 	alert("Please input Password.");
		// 	e.preventDefault();
		// 	return;
		// }
		$('#panel-cover').css("display", "block");
		$.ajax({
			url: $(this).attr('action'),
			type: 'post',
			method: 'post',
			data: $(this).serializeArray(),
			success: function(data, textStatus, jqXHR){
				switch($.parseJSON(data).status) {
					case 0:
					location.href = $.QueryString['next']?$.QueryString['next']:$.parseJSON(data).redirect;
					break;
					case 1:
					$('#panel-cover').css("display", "none");
					alert("Wrong Username or Password");
					break;
					case 2:
					$('#panel-cover').css("display", "none");
					alert("Account inactive.");
					break;
					default:
					break;
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
				alert("Error");
				if (errorThrown == "FORBIDDEN") {
					location.href = $('a#home').attr("href");
				}
			}
		});
		e.preventDefault();
	});
	if($('i#notifier').length != 0){
		//alert("Signed Out!");
	}
});
