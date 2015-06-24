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
		$(':checkbox').on('change.radiocheck', function() {
			bindingIpChangeEvent();
		});
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
			var parts = input.split('.');
			if(parts.length!=4){
				return false;
			}
			var last = parts.pop();
			parts = parts.concat(last.split('/'));
			for(var i=0;i<4;++i){
				var n = parts[i];
				if (n.length==0 || isNaN(n) || n<0 || n>255){
					return false;
				}
			}
			var n = parts[4];
			if(!n){
				return true;
			}else{
				if (n.length==0 || isNaN(n) || n<0 || n>32){
					return false;
				}
			}
			return true;
		}
		return false;
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
		$('label>:checkbox').radiocheck('check');
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
		if($(this).hasClass('fa-spinner')){
			e.preventDefault();
		}else{
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
		}
	});

	$("a[href='#proxySwitcher']").click(function(e){
		if($(this).hasClass('disabled')){
			e.preventDefault();
		}else{
			$(this).addClass('disabled');
			$(this).empty().append('Processing...');
			var action = 'switch';
			if($(this).text()=='Running'){
				action = 'stop';
			}else if($(this).text()=='Stopped'){
				action = 'start';
			}
			var data = $('#csrfForm').serializeArray();
			data.push(newObjectFactory('action', action));
			$.ajax({
				url: 'switch/',
				type: 'POST',
				data: data,
				success: function(data, textStatus, jqXHR){
					data = $.parseJSON(data);
					$("a[href='#proxySwitcher']").empty().append(data.status);
					$("a[href='#proxySwitcher']").removeClass('disabled');
					switch(data.code) {
						case 0:
						break;
						case 1:
						alert("Can't fetch proxy status, abort.");
						break;
						case 2:
						alert("Your balance is low, can't start Proxy.");
						break;
						default:
						alert('Report if you see this message. Error Code('+data.code + ')');
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
		}
	});

	$('#showProxyPass').click(function(){
		$(this).children('i').toggleClass('fa-eye').toggleClass('fa-eye-slash');
		if ($('#inputProxyPassword').attr('type') == 'password'){
			$('#inputProxyPassword').attr('type','text');
		} else {
			$('#inputProxyPassword').attr('type','password');
		}
		$('#inputProxyPassword').focus();
	});

	$('#changeProxyAuthBtn').click(function(){
		var password = $('#inputProxyPassword').prop('value');
		if (password == "") {
			alert("Empty Password is not Allowed.");
			return;
		}
		var data = $('#csrfForm').serializeArray();
		data.push(newObjectFactory('password', password));
		$.ajax({
			url: 'proxyauth/',
			type: 'POST',
			data: data,
			success: function(data, textStatus, jqXHR){
				data = $.parseJSON(data);
				$('#inputProxyPassword').prop('value','');
				switch(data.code){
					case 0:
					alert("Set successfully.");
					break;
					case 1:
					alert("Empty Password is not Allowd.");
					default:
					alert('Report if you see this message. Error Code('+data.code + ')');
					break;
				}
			},
			error: function(jqXHR, textStatus, errorThrown){
				alert("error");
				if (errorThrown == "FORBIDDEN") {
					location.href = $('a#home').attr("href");
				}
			}
		});
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
		var input = $('#addIpInput>.col-sm-3>input');
		if(!inputValidation(input.prop('value'),'ip')){
			alert('Invalid IP/IPset');
			return;
		}
		var ipCount = $('#bindIpBlock>div>label.checkbox').size();
		$('#addIpInput').before("<label class='checkbox biglabel' for='boxIp"+(ipCount)+"'><input type='checkbox' data-toggle='checkbox' value='0' id='boxIp"+(ipCount)+"' required></label>");
		var newIp = $('#addIpInput').prev().children(":checkbox");
		newIp.after(input.prop('value'));
		newIp.radiocheck('check');
		input.prop('value','');
		$('#addIpInput').hide();
		$('a#addIp').show();

		bindingIpChangeEvent();
		lastAdded++;
		e.preventDefault();
	});

	$('#addIpInput>.col-sm-3>input').keypress(function(e){
		if( e.which == 13){
			$('#addIpInput>.col-sm-9>.btn-success').click();
			e.preventDefault();
		}
	});

	$('#addIpInput>.col-sm-9>.btn-danger').click(function(e){
		var input = $('#addIpInput>.col-sm-3>input');
		input.prop('value','');
		$('#addIpInput').hide();
		$('a#addIp').show();
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
				data = $.parseJSON(data)
				switch(data.code){
					case 0:
					bindingIpChangeDone();
					break;
					case 1:
					alert("Wrong BindIP Choice.");
					break;
					case 2:
					alert("Invalid IP Address.");
					break;
					default:
					alert('Report if you see this message. Error Code('+data.code + ')');
					break;
				}
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
		$('label>:checkbox').radiocheck('uncheck');
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

	$("a[href='#refresh']").click();

});
