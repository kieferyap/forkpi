$(document).ready(function() {
	$(".tablesorter").tablesorter({
		widgets: ["filter"],
		sortReset      : true,
		sortRestart    : true,
		widgetOptions: {
			filter_childRows: false,
			filter_columnFilters: true,
			filter_ignoreCase: true,
			filter_searchDelay: 300,
			filter_startsWith: true,
			filter_saveFilters: true,
		}
	});

	var editableTextTrigger = false;
	var readyToClick = 1;
	var curListId = 0;

	$(document.body).on('click', '.editable-text', function(){
		if(editableTextTrigger){ // some other text is already being edited; close that first
			$('.editable-done').trigger('click');
			editableTextTrigger = false;
		}

		var current = $(this).html();
		
		if(current.trim() == '- - -'){
			current = '';
		}
		
		current = '<input type="text" class="editing-text col-md-8" value="'+current.trim()+'"/>';
		
		var doneButton = '<div class="completed-check editable-done"><span class="glyphicon glyphicon-ok-sign"></span></div>';
		
		if($(this).parent().attr('type') == 'rfid'){
			doneButton = '<div class="scan-edit-rfid"><span class="glyphicon glyphicon-search"></span></div>' + doneButton;
		}

		$(this).parent().html(current+doneButton);
		
		editableTextTrigger = true;
		
		$('.editing-text').on('click', function(e){
			e.stopPropagation();
		});
		
	}).on('click', '.editable-done', function(){
		var ajaxUrl = $(this).parent().attr('ajaxUrl');
		var ajaxId = $(this).parent().attr('ajaxId');
		var ajaxField = $(this).parent().attr('ajaxField');
		var ajaxValue = $(this).parent().children('input').val().replace('/', '&sol;').trim();
		var token = document.getElementsByName('csrfmiddlewaretoken')[0].value;

		$('.editing-text').off('click');
			
		editableTextTrigger = false;
		readyToClick = 1;
		
		var newValue = '<span class="editable-text">- - -</span>';
		
		if($(this).parent().children('input').val().trim() != ''){
			newValue = '<span class="editable-text">'+$(this).parent().children('input').val().trim()+'</span>';
		}
				
		$(this).parent().html(newValue);	

		$.ajax({
			type: 'POST',
			url: ajaxUrl,
			data: {
				'kid': ajaxId,
				'field': ajaxField,
				'value': ajaxValue,
				'csrfmiddlewaretoken': token
			},
			success: function(msg){
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
				location.reload();
			}
		});		
	}).on('click', '.scan-new-rfid, .scan-edit-rfid', function(e){
		ajaxUrl = '/addrfid';
		var isEditing = $(this).parent().attr('type') == 'rfid';

		var x = $(this);

		if(isEditing)
			textSelector = '.editing-text';
		else
			textSelector = '#inputUid';
	
		x.hide(256);	
		$(textSelector).val('Waiting for RFID data...');

		$.ajax({
			type: 'POST',
			url: ajaxUrl,
			data: {
				'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
			},
			success: function(msg){
				x.show(256);
				$(textSelector).val(msg);
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			}
		});
	});

	$(document.body).on('click', '.delete-btn', function(){
		deleteKeypair($(this).attr('id'))
	});
	$(document.body).on('click', '.deactivate-btn', function(){
		$(this).parent().parent().addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn btn-warning').addClass('activate-btn btn-success');
		$(this).html("Activate")
		toggleActiveKeypair($(this).attr('id'))
	});
	$(document.body).on('click', '.activate-btn', function(){
		$(this).parent().parent().removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn btn-warning').removeClass('activate-btn btn-success');
		$(this).html("Deactivate")
		toggleActiveKeypair($(this).attr('id'))
	});
});

function toggleActiveKeypair(kid){
	ajaxUrl = '/toggleactivekeypair';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'kid': kid,
			'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
		},
		success: function(msg){
		},
		error: function(msg){
			alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			location.reload();
		}
	});
}

function deleteKeypair(kid){
	$('#kp-'+kid).hide(256);

	ajaxUrl = '/deletekeypair';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'kid': kid,
			'csrfmiddlewaretoken': document.getElementsByName('csrfmiddlewaretoken')[0].value
		},
		success: function(msg){
		},
		error: function(msg){
			alert('Whoops, looks like something went wrong... Sorry \'bout that, let me refresh for you...');
			location.reload();
		}
	});
}
