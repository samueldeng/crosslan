$(document).ready(function(){
	$('#loginForm').submit(function(e){
		var pass = $("#id_password").prop("value");
		if(pass == "" || pass == $("#id_password").attr("value")){
			alert("Please input Password.");
			e.preventDefault();
			return;
		}
		$('#panel-cover').css("display", "block");
		$.ajax({
			url: $(this).attr('action'),
			type: 'POST',
			data: $(this).serializeArray(),
			success: function(data, textStatus, jqXHR){
				switch($.parseJSON(data).status) {
					case 0:
						location.href = $('a#logo').attr("href");
						break;
					case 1:
						$('#panel-cover').css("display", "none");
						alert("Wrong Username or Password");
						break;
					case 2:
						$('#panel-cover').css("display", "none");
						alert("Account disabled.");
						break;
					default:
						break;
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
				alert("Error");
				if (errorThrown == "FORBIDDEN") {
					location.href = $('a#logo').attr("href");
				}
			}
		});
		e.preventDefault();
	});
	$("input#id_username").focusin(function(){
		if(this.value == this.defaultValue){
			this.value = "";
			$(this).css("color", "#4c5356");
		}
	}).focusout(function(){
		if(this.value == ""){
			this.value = this.defaultValue;
			$(this).css("color", "");
		}
	});
	$("input#id_password").focusin(function(){
		if(this.value == this.defaultValue){
			this.value = "";
			this.type = "password";
			$(this).css("color", "#4c5356");
		}
	}).focusout(function(){
		if(this.value == ""){
			this.value = this.defaultValue;
			this.type = "text";
			$(this).css("color", "");
		}
	});
});
