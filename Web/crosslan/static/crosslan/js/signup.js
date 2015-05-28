$(document).ready(function(){
	$('#inputUsername').focus();
	$('#formSignup').submit(function(e){
		$('#panel-cover').css('display', 'block');
		$.ajax({
			url: $(this).attr('action'),
			type: 'POST',
			data: $(this).serializeArray(),
			success: function(data, textStatus, jqXHR){
				switch($.parseJSON(data).status) {
					case 0:
					location.href = $.parseJSON(data).redirect;
					break;
					case 1:
					//TODO: Validate input on front side, too.
					$('#panel-cover').css('display', 'none');
					alert('Invalid Input');
					break;
					case 2:
					$('#panel-cover').css('display', 'none');
					alert('Username Taken');
					break;
					case 3:
					$('#panel-cover').css('display', 'none');
					alert('Invalid Redeem Code');
					break;
					case 4:
					$('#panel-cover').css('display', 'none');
					alert('Redeem Code used');
					default:
					$('#panel-cover').css('display', 'none');
					alert('Signup failed. Report if you see this message. Error Code('+$.parseJSON(data).status + ')');
					break;
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
				alert('Error');
				if (errorThrown == 'FORBIDDEN') {
					location.href = $('a#home').attr('href');
				}
			}
		});
		e.preventDefault();
	});
	$('#showPass').click(function(){
		$(this).children('i').toggleClass('fa-eye').toggleClass('fa-eye-slash');
		if ($('#inputPassword').attr('type') == 'password'){
			$('#inputPassword').attr('type','text');
		} else {
			$('#inputPassword').attr('type','password');
		}
		$('#inputPassword').focus();
	})
});
