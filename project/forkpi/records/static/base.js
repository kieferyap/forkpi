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
		ajaxUrl = '/keypairs/scanrfid';
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

	// For keypairs
	$(document.body).on('click', '.delete-btn', function(){
		deleteKeypair($(this).attr('id'));
	});
	$(document.body).on('click', '.deactivate-btn', function(){
		$(this).parent().parent().addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn btn-warning').addClass('activate-btn btn-success');
		$(this).html("Activate");
		toggleActiveKeypair($(this).attr('id'));
	});
	$(document.body).on('click', '.activate-btn', function(){
		$(this).parent().parent().removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn btn-warning').removeClass('activate-btn btn-success');
		$(this).html("Deactivate");
		toggleActiveKeypair($(this).attr('id'));
	});
	// For users
	// Deactivate
	$(document.body).on('click', '.deactivate-btn-user', function(){
		$(this).parent().parent().addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn-user btn-warning').addClass('activate-btn-user btn-success');
		$(this).html("Activate");
		toggleActiveUser($(this).attr('id'));
	});
	// Activate
	$(document.body).on('click', '.activate-btn-user', function(){
		$(this).parent().parent().removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn-user btn-warning').removeClass('activate-btn-user btn-success');
		$(this).html("Deactivate");
		toggleActiveUser($(this).attr('id'));
	});
	// Demote
	$(document.body).on('click', '.demote-btn-user', function(){
		$('#star-'+$(this).attr('id')).hide();
		$(this).removeClass('demote-btn-user btn-warning').addClass('promote-btn-user btn-success');
		$(this).html("Promote to Admin");
		toggleStaff($(this).attr('id'));
	});
	// Promote
	$(document.body).on('click', '.promote-btn-user', function(){
		$('#star-'+$(this).attr('id')).show();
		$(this).addClass('demote-btn-user btn-warning').removeClass('promote-btn-user btn-success');
		$(this).html("Demote to Regular");
		toggleStaff($(this).attr('id'));
	});
	// Deny -- which is the same as delete, for now.
	$(document.body).on('click', '.deny-btn-user', function(){
		deleteUser($(this).attr('id'));
	});
	// Approve
	$(document.body).on('click', '.approve-btn-user', function(){
		$(this).parent().parent().removeClass('redded');
		var promoteButton = '<button class="btn btn-success promote-btn-user" id="'+$(this).attr('id')+'">Promote to Admin</button> ';
		var deactivateButton = '<button class="btn btn-warning deactivate-btn-user" id="'+$(this).attr('id')+'">Deactivate</button> ';
		var deleteButton = '<button class="btn btn-danger delete-btn-user" id="'+$(this).attr('id')+'">Delete</button>';
		$(this).parent().html(promoteButton + deactivateButton + deleteButton);
		$('#unapproved-'+$(this).attr('id')).hide();
		approveUser($(this).attr('id'));
	});
	// Delete
	$(document.body).on('click', '.delete-btn-user', function(){
		deleteUser($(this).attr('id'));
	});
});


// For users
function toggleActiveUser(uid){
	ajaxUrl = '/users/toggleactiveuser';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'uid': uid,
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


function toggleStaff(uid){
	ajaxUrl = '/users/togglestaff';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'uid': uid,
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

function approveUser(uid){
	ajaxUrl = '/users/approveuser';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'uid': uid,
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

function deleteUser(uid){
	$('#user-'+uid).hide(256);
	ajaxUrl = '/users/delete';

	$.ajax({
		type: 'POST',
		url: ajaxUrl,
		data: {
			'uid': uid,
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



// For keypairs
function toggleActiveKeypair(kid){
	ajaxUrl = '/keypairs/toggleactive';

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

	ajaxUrl = '/keypairs/delete';

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
