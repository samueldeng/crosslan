$(document).ready(function(){
	function enableBindIp(){
		block = $('#bindIpBlock');
		block.removeClass('disabled');
		block.find("label>input").radiocheck('enable');
		$('a#addIp').removeClass('disabled');
	}

	function disableBindIp(){
		block = $('#bindIpBlock');
		block.addClass('disabled');
		block.find("label>input").radiocheck('disable');
		$('a#addIp').addClass('disabled');
	}

	function bindingIpChangeEvent(){
		$('#binding').addClass('changed');
		$('#changeSubmitWrapper').show();
	}

	function bindingIpChangeDone(){
		$('#binding').removeClass('changed');
		$('#changeSubmitWrapper').hide();
	}

	function newObjectFactory(name, value){
		var ob = new Object();
		ob.name = name;
		ob.value = value;
		return ob;
	}

	function getCheckedIp(){
		var ids = [];
		var labels = $('#bindIpBlock>div>label');
		for(var i=0;i<labels.length;++i){
			if($(labels[i]).children('input').prop('checked')){
				ids.push($(labels[i]).prop('for'));
			}
		}
		return ids;
	}

	function inputValidation(input, type){
		if(type=="ip"){

		}
		return true;
	}

	{
		// Initializing
		lastBind = true;
		lastAdded = 0;
		lastIp = [];
		var checked = true;
		if($('#bindingSwitch').prop('value')=='0'){
			checked = false;
			lastBind = false;
		}
		$('#bindingSwitch').switchButton({
			checked: checked,
			labels_placement: "right",
			width: 40,
			height: 20,
			button_width: 20,
		});
		$(':checkbox').radiocheck('check');
		if(!checked){
			disableBindIp();
		}
		lastIp = getCheckedIp()
	}
	// Event Listeners
	$(document).scroll(function(){
		nav = $('nav.side-nav');
		info = $('#infoContent');
		toTop = $(document).scrollTop();
		if(!nav.hasClass('side-nav-fixed') && toTop > 92){
			nav.toggleClass('side-nav-fixed');
			info.toggleClass('col-md-offset-3');
		}else if(nav.hasClass('side-nav-fixed') && toTop < 92){
			nav.toggleClass('side-nav-fixed');
			info.toggleClass('col-md-offset-3');
		}
	});
	$('#bindingSwitchWrapper').click(function(){
		if($('#bindingSwitch').prop('checked')){
			enableBindIp();
		}else{
			disableBindIp();
		}
		bindingIpChangeEvent();
	});
	$('#bindingSwitchWrapper').find('div, span').click(function(){
		$('#bindingSwitchWrapper').click();
	});

	$("a[href='#refresh']").click(function(e){
		$(this).children('i').toggleClass('fa-refresh fa-spinner fa-pulse');
		$.ajax({
			url: 'refresh/',
			type: 'GET',
			success: function(data, textStatus, jqXHR){
				data = $.parseJSON(data);
				$('#proxyHostLabel').next().children('a').empty().append(data['host']);
				$('#proxyStatusLabel').next().children('a').empty().append(data['status']);
				$('#balanceLabel').next().children('a').empty().append(data['balance']);
				$("a[href='#refresh']").children('i').toggleClass('fa-refresh fa-spinner fa-pulse');
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

	$(':checkbox').on('change.radiocheck', function() {
		bindingIpChangeEvent();
  	});

	$('a#addIp').click(function(e){
		if($(this).hasClass('disabled')){
			e.preventDefault();
		}else{
			addIpBox = $(this).prev();
			$(this).toggle();
			addIpBox.toggle();
			addIpBox.find('input').focus();
			e.preventDefault();
		}
	});

	$('#addIpInput>.col-sm-9>.btn-success').click(function(e){
		var ipCount = $('#bindIpBlock>div>label.checkbox').size();
		$('#addIpInput').before("<label class='checkbox biglabel' for='boxIp"+(ipCount)+"'><input type='checkbox' data-toggle='checkbox' value='0' id='boxIp"+(ipCount)+"' required></label>");
		var newIp = $('#addIpInput').prev().children(":checkbox");
		var input = $('#addIpInput>.col-sm-3>input');
		newIp.after(input.prop('value'));
		newIp.radiocheck();
		if(!$('#bindingSwitch').prop('checked')){
			newIp.radiocheck('disable');
		}else{
			newIp.radiocheck('check');
		}
		input.prop('value','');
		$('#addIpInput').toggle();
		$('a#addIp').toggle();

		bindingIpChangeEvent();
		lastAdded++;
		e.preventDefault();
	});

	$('#addIpInput>.col-sm-9>.btn-danger').click(function(e){
		var input = $('#addIpInput>.col-sm-3>input');
		input.prop('value','');
		$('#addIpInput').toggle();
		$('a#addIp').toggle();
		e.preventDefault();
	});

	$('#changeSubmitWrapper').find('button').click(function(e){
		bind = $('#bindingSwitch').prop('checked');
		var ips = [];
		var labels = $('#bindIpBlock>div>label');
		for(var i=0;i<labels.length;++i){
			if($(labels[i]).children('input').prop('checked')){
				ips.push($(labels[i]).text().trim());
			}
		}
		if(ips.length==0){
			alert("You're not choosing any IP.");
			return;
		}
		ips[0] = ips[0].split(" ")[0];	// Remove "(Current IP)" from the 1st
		var data = $('#csrfForm').serializeArray();
		data.push(newObjectFactory('bind', bind));
		data.push(newObjectFactory('ips', ips));
		$.ajax({
			url: 'rebind/',
			type: 'POST',
			data: data,
			success: function(data, textStatus, jqXHR){
				bindingIpChangeDone();
			},
			error: function(jqXHR, textStatus, errorThrown){
				alert("error");
				if (errorThrown == "FORBIDDEN") {
					location.href = $('a#home').attr("href");
				}
			}
		});

		// Update last*
		lastAdded = 0;
		lastBind = bind;
		lastIp = getCheckedIp();
		e.preventDefault();
	});

	$('#changeSubmitWrapper').find('a').click(function(e){
		$(':checkbox').radiocheck('uncheck');
		for(var i=0;i<lastIp.length;++i){
			$('#'+lastIp[i]).radiocheck('check');
		}
		if(lastBind != $('#bindingSwitch').prop('checked')){
			$('#bindingSwitch').switchButton({checked:lastBind});
			if(lastBind){
				enableBindIp();
			}else{
				disableBindIp();
			}
		}
		if(lastAdded>0){
			$("#bindIpBlock>div>label").slice(-lastAdded).remove();
		}
		lastAdded = 0;

		bindingIpChangeDone();
		e.preventDefault();
	});

});
