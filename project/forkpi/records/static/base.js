// For table sorting and filtering
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
			filter_startsWith: false,
			filter_saveFilters: true,
		}
	});
});

// For editing text
$(document).ready(function() {
	var editableTextTrigger = false;

	$(document.body).on('click', '.editable-text', function(){
		if(editableTextTrigger){ // some other text is already being edited; close that first
			$('.editable-done').trigger('click');
			editableTextTrigger = false;
		}

		var current = $(this).html();
		var parent = $(this).parent();
		var type = parent.attr('type');
		if(current.trim() == '- - -'){
			current = '';
		}
		
		if (type == 'edit-keypair-doors') {
			current = '<input type="text" class="editing-text col-md-8" value=""/>';
		} else {
			current = '<input type="text" class="editing-text col-md-8" value="'+current.trim()+'"/>';
		}
		
		var doneButton = '<div class="completed-check editable-done"><span class="glyphicon glyphicon-ok-sign"></span></div>';
		
		if (parent.attr('type') == 'edit-rfid') {
			doneButton = '<div class="scan-edit-rfid"><span class="glyphicon glyphicon-search"></span></div>' + doneButton;
		} else if (type == 'edit-fingerprint') {
			doneButton = '<div class="scan-edit-fingerprint"><span class="glyphicon glyphicon-search"></span></div>' + doneButton;
		}

		parent.html(current + doneButton);
		editableTextTrigger = true;

		if (type == 'edit-keypair-doors') {
			var kid = parent.attr('ajaxId');
			var doors = eval(parent.attr('ajaxData'));

			$('.editing-text').tokenInput('/doors/search/', {
				theme: 'facebook',
				hintText: null,
				prePopulate: doors,
				preventDuplicates : true,
				onAdd: linkDoorToKeypair(kid),
				onDelete: unlinkDoorFromKeypair(kid),
			});
			var searchBox = parent.find('ul');
			searchBox.addClass('col-md-10');
			searchBox.click();
		} else {
			var textBox = parent.find('input');
			textBox.focus();
			textBox.select();
		}
		
		$('.editing-text').on('click', function(e){
			e.stopPropagation();
		});
		
	}).on('click', '.editable-done', function(){
		
		var parent = $(this).parent();
		var type = parent.attr('type');
		var ajaxId = parent.attr('ajaxId');

		var newValue = '<span class="editable-text">';

		if (type == 'edit-keypair-doors') {
			doors_json_new = $('.editing-text').tokenInput('get');
			parent.attr('ajaxData', JSON.stringify(doors_json_new));
			var len = doors_json_new.length;
			if (len == 0) {
				newValue += '- - -';
			} else {
				for (var i = 0; i < len; i++) {
					newValue += '<li class="token-input-token-facebook">' + doors_json_new[i].name + '</li>'
				}
			}
		} else {
			var ajaxUrl = parent.attr('ajaxUrl');
			var ajaxValue = parent.children('input').val().trim();
			
			if(ajaxValue == '') {
				newValue += '- - -';
			} else {
				newValue += ajaxValue;
			}

			$.ajax({
				type: 'POST',
				url: ajaxUrl,
				data: {
					'kid': ajaxId,
					'value': ajaxValue,
					'csrfmiddlewaretoken': getToken()
				},
				success: function(msg){
				},
				error: function(msg){
					alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
					location.reload();
				}
			});	
		}

		newValue += '</span>';	
		parent.html(newValue);
		editableTextTrigger = false;
		$('.editing-text').off('click');

	}).on('click', '.scan-new-rfid, .scan-edit-rfid', function(e){
		ajaxUrl = '/keypairs/scan/rfid';
		var isEditing = $(this).parent().attr('type') == 'edit-rfid';

		if(isEditing)
			textSelector = '.editing-text';
		else
			textSelector = '#inputUid';
		
		var scan_button = $(this);
		scan_button.hide(256);	
		$(textSelector).val('Waiting for RFID data...');

		$.ajax({
			type: 'POST',
			url: ajaxUrl,
			data: {
				'csrfmiddlewaretoken': getToken()
			},
			success: function(msg){
				scan_button.show(256);
				$(textSelector).val(msg);
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			}
		});
	}).on('click', '.scan-new-fingerprint, .scan-edit-fingerprint', function(e){
		ajaxUrl = '/keypairs/scan/fingerprint';
		var isEditing = $(this).parent().attr('type') == 'edit-fingerprint';

		if(isEditing)
			textSelector = '.editing-text';
		else
			textSelector = '#inputFinger';
	
		var scan_button = $(this);
		scan_button.hide(256);	
		$(textSelector).val('Waiting for finger...');

		$.ajax({
			type: 'POST',
			url: ajaxUrl,
			data: {
				'csrfmiddlewaretoken': getToken()
			},
			success: function(msg){
				scan_button.show(256);
				$(textSelector).val(msg);
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			}
		});
	});

	// For keypairs
	$(document.body).on('click', '.delete-btn', function(){
		deleteKeypair($(this).attr('id'));
	});
	$(document.body).on('click', '.deactivate-btn', function(){
		toggleActiveKeypair($(this).attr('id'));
		$(this).parent().parent().parent().parent().addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn btn-warning').addClass('activate-btn btn-success');
		$(this).html("Activate");
	});
	$(document.body).on('click', '.activate-btn', function(){
		toggleActiveKeypair($(this).attr('id'));
		$(this).parent().parent().parent().parent().removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn btn-warning').removeClass('activate-btn btn-success');
		$(this).html("Deactivate");
	});
	// For users
	// Deactivate
	$(document.body).on('click', '.deactivate-btn-user', function(){
		toggleActiveUser($(this).attr('id'));
		$(this).parent().parent().parent().parent().addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn-user btn-warning').addClass('activate-btn-user btn-success');
		$(this).html("Activate");
	});
	// Activate
	$(document.body).on('click', '.activate-btn-user', function(){
		toggleActiveUser($(this).attr('id'));
		$(this).parent().parent().parent().parent().removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn-user btn-warning').removeClass('activate-btn-user btn-success');
		$(this).html("Deactivate");
	});
	// Demote
	$(document.body).on('click', '.demote-btn-user', function(){
		toggleStaff($(this).attr('id'));
		$(this).html("Promote");
		$('#star-'+$(this).attr('id')).hide();
		$(this).removeClass('demote-btn-user btn-warning').addClass('promote-btn-user btn-success');
	});
	// Promote
	$(document.body).on('click', '.promote-btn-user', function(){
		toggleStaff($(this).attr('id'));
		$('#star-'+$(this).attr('id')).show();
		$(this).addClass('demote-btn-user btn-warning').removeClass('promote-btn-user btn-success');
		$(this).html("Demote");
	});
	// Deny -- which is the same as delete, for now.
	$(document.body).on('click', '.deny-btn-user', function(){
		deleteUser($(this).attr('id'));
	});
	// Approve
	$(document.body).on('click', '.approve-btn-user', function(){
		approveUser(uid);
		var uid = $(this).attr('id');
		$(this).parent().parent().parent().parent().removeClass('redded');
		var promoteButton = '<button class="btn btn-success promote-btn-user" id="'+uid+'">Promote</button> ';
		var deactivateButton = '<button class="btn btn-warning deactivate-btn-user" id="'+uid+'">Deactivate</button> ';
		var deleteButton = '<button class="btn btn-danger delete-btn-user" id="'+uid+'">Delete</button>';
		$(this).parent().parent().html(wrapButton(promoteButton) + wrapButton(deactivateButton) + wrapButton(deleteButton));
		$('#unapproved-'+$(this).attr('id')).hide();
	});
	// Delete
	$(document.body).on('click', '.delete-btn-user', function(){
		deleteUser($(this).attr('id'));
	});
});


function wrapButton(buttonHtml) {
	return '<div class="btn-group btn-group-justified" role="group">' + buttonHtml + '</div>';
}
				
var linkDoorToKeypair = function(kid) {
	return function(door) {
		ajaxUrl = '/keypairs/link_door';
		postToUrl(ajaxUrl, {kid:kid, did:door.id})
	}
}

var unlinkDoorFromKeypair = function(kid) {
	return function(door) {
		ajaxUrl = '/keypairs/unlink_door';
		postToUrl(ajaxUrl, {kid:kid, did:door.id})
	}
}

function toggleActiveUser(uid){
	ajaxUrl = '/users/toggleactive';
	postToUrl(ajaxUrl, {'uid':uid});
}

function toggleStaff(uid){
	ajaxUrl = '/users/togglestaff';
	postToUrl(ajaxUrl, {'uid':uid});
}

function approveUser(uid){
	ajaxUrl = '/users/approve';
	postToUrl(ajaxUrl, {'uid':uid});
}

function deleteUser(uid){
	$('#user-'+uid).hide(256);
	ajaxUrl = '/users/delete';
	postToUrl(ajaxUrl, {'uid':uid});
}


function toggleActiveKeypair(kid){
	ajaxUrl = '/keypairs/toggleactive';
	postToUrl(ajaxUrl, {'kid':kid});
}

function deleteKeypair(kid) {
	$('#kp-'+kid).hide(256);
	ajaxUrl = '/keypairs/delete';
	postToUrl(ajaxUrl, {'kid':kid});
}

function getToken() {
	return document.getElementsByName('csrfmiddlewaretoken')[0].value;
}

function postToUrl(url, data) {
	data['csrfmiddlewaretoken'] = getToken();
	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: data,
		success: function(msg){
		},
		error: function(msg){
			alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			location.reload();
		}
	});
}