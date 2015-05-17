$(document).ready(function(){
	$('#urlForm').submit(function(e){
		var origin = $('#id_originUrl').prop("value");
		if(origin == "" || origin == $('#id_originUrl').attr("value")){
			alert("Please input the url to be shortened.");
			e.preventDefault();
			return;
		}
		$('#panel-cover').css("display", "block");
		alert("Submited")
		$.ajax({
			url: $(this).attr('action'),
			type: 'POST',
			data: $(this).serializeArray(),
			success: function(data, textStatus, jqXHR){
				if($.parseJSON(data).status == 1){
					$('#id_shortUrl').val($.parseJSON(data).result);
				}else{
					$('#panel-cover').css("display", "none");
					alert($.parseJSON(data).result);
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
			}
		});
		e.preventDefault();
	});

	$('#id_shortUrl').focusin(function(){
		this.select();
	}).focusout(function(){
		this.unselect()
	});
});
