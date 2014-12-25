$(document).ready(function() {
	var editableTextTrigger = false;
	var readyToClick = 1;
	var curListId = 0;

	$(document.body).on('click', '.editable-text', function(){
		var current = $(this).html();
		
		if(current.trim() == '- - -'){
			current = '';
		}
		
		current = '<input type="text" class="editing-text col-md-8" value="'+current.trim()+'"/>';
		
		var doneButton = '&nbsp;<div class="completed-check editable-done"><span class="glyphicon glyphicon-ok-sign"></span></div>';
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
				alert('Whoops, looks like something went wrong... Sorry \'bout that, could you please refresh for me?')
			}
		});		
	});

	$(document).on('click', function(e){
		if(editableTextTrigger){
			readyToClick -= 1;
		}
		if(readyToClick < 0){
			$('.editable-done').trigger('click');
			$('.editable-textarea-done').trigger('click');
		}
	});

	$(document.body).on('click', '.delete-btn', function(){
		deleteKeypair($(this).attr('id'))
	});
});

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
			alert('Whoops, looks like something went wrong... Sorry \'bout that, could you please refresh for me?');
		}
	});
}
