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

	$('#newDoors').tokenInput($('#newDoors').parent().data('search-url'), {
		theme: 'facebook',
		hintText: 'Type a door name...',
		prePopulate: null,
		preventDuplicates : true
	});
});


// For editing text
$(document).ready(function() {
	// some text is being edited
	var editableTextTrigger = false;

	// some editing text in the modal was opened
	var editedTextInModal = false;

	// Editing text
	$(document.body).on('click', '.editable-text', function(){
		if (editableTextTrigger) { // some other text is already being edited; close that first
			$('.editable-done').trigger('click');
			editableTextTrigger = false;
		}
		// we are editing another textbox
		editableTextTrigger = true;

		var newHtml = ''; // the HTML that will replace this element

		var parent = $(this).parent();
		var field = parent.data('field');
		
		// these fields are in the modal
		if (field == 'pin' || field == 'rfid' || field == 'fingerprint') {
			editedTextInModal = true;
		}


		// generate the textbox that will replace this element
		var currentValue = $(this).html().trim();
		if (currentValue == '- - -') {
			currentValue = ''; // effectively blank
		} else if (field == 'doors' || field == 'keypairs') {
			currentValue = ''; // the textbox should be empty because we will replace it later
		}
		newHtml += '<input type="text" class="editing-text col-md-8" value="' + currentValue + '" />';
		
		if (field == 'rfid' || field == 'fingerprint') {
			var scanButton = '<div class="scan-edit"><span class="glyphicon glyphicon-search"></span></div>';
			newHtml += scanButton;
		}

		var doneButton = '<div class="completed-check editable-done"><span class="glyphicon glyphicon-ok-sign"></span></div>';
		newHtml += doneButton;

		parent.html(newHtml);

		if (field == 'doors' || field == 'keypairs') {
			// replace the textbox with tokenInput

			var my_id = parent.data('id');
			var links = eval(parent.data('value'));
			var searchUrl = parent.data('search-url');

			$('.editing-text').tokenInput(searchUrl, {
				theme: 'facebook',
				hintText: null,
				prePopulate: links,
				preventDuplicates : true,
				onAdd: function(link) {
					postUrl = parent.data('link-url');
					postToUrl(postUrl, {my_id:my_id, link_id:link.id});
				},
				onDelete: function(link) {
					postUrl = parent.data('unlink-url');
					postToUrl(postUrl, {my_id:my_id, link_id:link.id});
				},
			});
			// the textbox will be replaced by a ul element, which we need to resize
			var searchBox = parent.find('ul');
			searchBox.addClass('col-md-10');
			// put the cursor inside the search box
			searchBox.click();
		} else {
			var textBox = parent.find('input');
			// put the cursor inside the text box
			textBox.focus();
			// highlight everything inside the text box
			textBox.select();
		}
		
	}).on('click', '.editable-done', function() {
		var parent = $(this).parent();
		var field = parent.data('field');

		var newHtml = '<span class="editable-text">';

		if (field == 'doors' || field == 'keypairs') {
			var newDoors = $('.editing-text').tokenInput('get');
			parent.data('value', JSON.stringify(newDoors));

			var len = newDoors.length;
			if (len == 0) {
				newHtml += '- - -';
			} else {
				for (var i = 0; i < len; i++) {
					newHtml += '<li class="token-input-token-facebook">' + newDoors[i].name + '</li>'
				}
			}
			// no need to send changes to server since it was already sent while editing (see onAdd and onDelete)

		} else {
			var newValue = parent.children('input').val().trim();
			parent.data('value', newValue);
			
			if (newValue == '') {
				newHtml += '- - -';
			} else {
				newHtml += newValue;
			}
			newHtml += '</span>';
			
			// send changes to server
			var id = parent.data('id');
			var postUrl = parent.data('post-url');
			postToUrl(postUrl, {id:id, value:newValue}, function() {
				// for correctness the HTML must only be updated on success, 
				// but it is less responsive
				// parent.html(newHtml);
			});
		}
		newHtml += '</span>';
		parent.html(newHtml);

		editableTextTrigger = false;
		// $('.editing-text').off('click');

	});

	$(window).bind('beforeunload', function(){
		if (editableTextTrigger) { // some text is being edited -> confirm first
			return 'Are you sure you want to leave?';
		}
	});

	// Scanning RFID and Fingerprints
	$(document.body).on('click', '.scan-new, .scan-edit', function(e){
		var scanButton = $(this);
		var parent = $(this).parent();
		var target = parent.data('target-textbox');

		var placeholder = '';
		var field = parent.data('field');
		if (field == 'rfid') {
			placeholder = 'Waiting for RFID data...';
		} else if (field == 'fingerprint') {
			alert("WARNING: Please pay close attention to the fingerprint scanner:\n"
				+"1. PRESS FINGER on the scanner when it LIGHTS UP. (Blue light)\n"
				+"2. REMOVE FINGER when the LIGHT GOES OFF.\n"
				+"3. You will need to press your finger THREE TIMES.\n"
				+"This is for a higher matching accuracy. Thank you very much for understanding.");
			placeholder = 'Waiting for finger...';
		}

		// Clear target textbox and replace with placeholder
		$(target).val('');
		$(target).attr('placeholder', placeholder);

		scanButton.hide(256);
		$.ajax({
			type: 'POST',
			url: parent.data('scan-url'),
			data: {
				csrfmiddlewaretoken: getToken()
			},
			success: function(msg) {
				scanButton.show(256);
				$(target).val(msg);
				$(target).attr('placeholder', '');
			},
			error: function(msg) {
				// nothing was scanned: show error as textbox placeholder
				scanButton.show(256);
				$(target).attr('placeholder', msg['responseText'])
			}
		});
	});

	// Keypair and User Actions
	$(document.body).on('click', '.activate-btn', function(){
		var btn = $(this);
		postIdToUrlInParent(btn, function(msg) {
			btn.closest('tr').removeClass('greyed'); // ungrey the corresponding row
			btn.addClass('deactivate-btn btn-warning').removeClass('activate-btn btn-success');
			btn.html("Deactivate");
		});

	}).on('click', '.deactivate-btn', function(){
		var btn = $(this);
		postIdToUrlInParent(btn, function(msg) {
			btn.closest('tr').addClass('greyed'); // grey out the corresponding row
			btn.removeClass('deactivate-btn btn-warning').addClass('activate-btn btn-success');
			btn.html("Activate");
		});

	}).on('click', '.delete-btn, .deny-btn', function(){
		var btn = $(this);
		postIdToUrlInParent(btn, function(msg) {
			btn.closest('tr').hide(256);
		});
	}).on('click', '.edit-btn', function(){
		var parent = $(this).parent();
		var id = parent.data('id');
		var name = $('#name-'+id).parent().data('value');

		if($('#pin-'+id).parent().data('value') != '') {

			var modalHeaderCloseBtn = '<span aria-hidden="true">&times;</span>';
			var modalHeaderCloseContainer = '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'+modalHeaderCloseBtn+'</button>';
			var modalHeaderText = '<h4 class="modal-title" id="edit-modalLabel">Enter PIN of user ('+name+'):</h4>';

			var modalFooterCloseBtn = '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';
			var modalFooterSubmitBtn = '<button type="button" class="btn btn-primary pin-authenticate-btn">Submit</button>';
			var modalBodyInput = 'Enter PIN: <input type="password" class="modal-pin" id="modal-pin"></input>';

			var modalBody = '<span data-post-url="/keypairs/authenticate_pin" data-id="'+id+'">'+modalBodyInput+'</span>';
			var modalFooter = modalFooterCloseBtn + " " + modalFooterSubmitBtn;
			var modalHeader = modalHeaderCloseContainer + modalHeaderText;

			$('#edit-modal > .modal-dialog > .modal-content > .modal-body').html(modalBody);
			$('#edit-modal > .modal-dialog > .modal-content > .modal-footer').html(modalFooter);
			$('#edit-modal > .modal-dialog > .modal-content > .modal-header').html(modalHeader);

		} else {
			editKeypair(id); 
		}

	}).on('click', '.pin-authenticate-btn', function(){
		var parent = $('.modal-pin').parent();
		var id = parent.data('id');
		var modalBodyInput = 'Enter PIN: <input type="password" class="modal-pin"></input>';
		var originalModalBody = '<span data-post-url="/keypairs/authenticate_pin" data-id="'+id+'">'+modalBodyInput+'</span>';

		postIdToUrlInParent($('.modal-pin'), function(msg) {
			if(msg.trim() != ''){
				editKeypair(msg);
			}
			else{
				var errorMessage = '<div class="alert alert-error">Incorrect PIN</div>';
				var modalBody = errorMessage + originalModalBody;
				$('#edit-modal > .modal-dialog > .modal-content > .modal-body').html(modalBody);
			}
		});
	});

	// On edit modal close
	$('#edit-modal').on('hidden.bs.modal', function () {
		if (editedTextInModal) {
			location.reload();
		}
	});

	// Additional User Actions
	$(document.body).on('click', '.approve-btn', function(){
		var parent = $(this).parent();
		$.ajax({
			type: 'POST',
			url: parent.data('post-url'),
			data: {
				id: parent.data('id'),
				csrfmiddlewaretoken: getToken(),
			},
			success: function(msg){
				// need to update user action buttons and the number of unapproved users in the navbar
				location.reload()
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
				location.reload();
			}
		});

	}).on('click', '.demote-btn', function(){
		var btn = $(this);
		var id = $(this).parent().data('id');
		postIdToUrlInParent(btn, function() {
			$('#star-' + id).hide();
			btn.removeClass('demote-btn btn-warning').addClass('promote-btn btn-success');
			btn.html("Promote");
		});
	}).on('click', '.promote-btn', function(){
		var btn = $(this);
		var id = $(this).parent().data('id');
		postIdToUrlInParent(btn, function() {
			$('#star-' + id).show();
			btn.addClass('demote-btn btn-warning').removeClass('promote-btn btn-success');
			btn.html("Demote");
		});
	});
});

function getToken() {
	return document.getElementsByName('csrfmiddlewaretoken')[0].value;
}

function postToUrl(postUrl, data, onSuccess) {
	data['csrfmiddlewaretoken'] = getToken();
	$.ajax({
		type: 'POST',
		url: postUrl,
		data: data,
		success: onSuccess,
		error: function(msg){
			alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			location.reload();
		}
	});
}

function postIdToUrlInParent(element, onSuccess) {
	var parent = element.parent();
	var id = parent.data('id');
	var postUrl = parent.data('post-url');
	var val = $(element).val();
	postToUrl(postUrl, {id:id, val:val}, onSuccess);
}

function editKeypair(id, msg){
	var arr = JSON.pase(msg);

	var name = $('#name-'+id).html().trim();
	var modalHeaderCloseBtn = '<span aria-hidden="true">&times;</span>';
	var modalHeaderCloseContainer = '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'+modalHeaderCloseBtn+'</button>';
	var modalHeaderText = '<h4 class="modal-title" id="edit-modalLabel">'+name+'\'s Credentials</h4>';

	var userPIN = arr['pin'];
	var userRFID = arr['rfid_uid'];
	var userFING = arr['fingerprint_template'];

	if(!userPIN){userPIN = '- - -';}
	if(!userRFID){userRFID = '- - -';}
	if(!userFING){userFING = '- - -';}

	var bodyPIN = 
		'<div style="font-weight: bold">PIN:</div>'+
		'<span class="edit-pin"'+
			'data-post-url="'+$('#post-url-pin').val()+'"'+
			'data-field="pin"'+
			'data-id="'+id+'" data-value="'+userPIN+'">'+
			'<span class="editable-text" id="pin-'+id+'">'+
				userPIN+
			'</span>'+
		'</span>'+
		'<hr style="clear:both;"/>';

	var bodyRFID = 
		'<div style="font-weight: bold">RFID UID:</div>'+
		'<span class="edit-rfid"'+
			'data-post-url="'+$('#post-url-rfid').val()+'" data-scan-url="'+$('#scan-url-fingerprint').val()+'"'+
			'data-field="rfid" data-target-textbox=".editing-text"'+
			'data-id="'+id+'" data-value="'+userRFID+'">'+
			'<span class="editable-text">'+
				userRFID+
			'</span>'+
		'</span>'+
		'<hr style="clear:both;"/>';

	var bodyFING = 
		'<div style="font-weight: bold">Fingerprint:</div>'+
		'<span class="edit-fingerprint"'+
			'data-post-url="'+$('#post-url-fingerprint').val()+'" data-scan-url="'+$('#scan-url-fingerprint').val()+'"'+
			'data-field="/keypairs/edit/fingerprint" data-target-textbox=".editing-text"'+
			'data-id="'+id+'" data-value="'+userFING+'">'+
			'<span class="editable-text">'+
				userFING+
			'</span>'+
		'</span>'+
		'<hr style="clear:both;"/>';

	var modalBody = bodyPIN + bodyRFID + bodyFING
	var modalHeader = modalHeaderCloseContainer + modalHeaderText;
	var modalFooter = '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>';

	$('#edit-modal > .modal-dialog > .modal-content > .modal-header').html(modalHeader);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-footer').html(modalFooter);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body').html(modalBody);
}