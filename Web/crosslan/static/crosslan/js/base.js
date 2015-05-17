$(document).ready(function(){
	$("a#login").click(function(){
		location.href = $(this).attr("value");
	});
	$("a#logout").click(function(){
		location.href = $(this).attr("value");
	});

	$("input.innerLabel").focusin(function(){
		if(this.value == this.defaultValue){
			this.value = "";
		}
	}).focusout(function(){
		if(this.value == ""){
			this.value = this.defaultValue;
		}
	});
});
