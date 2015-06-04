// For table sorting and filtering
$(document).ready(function() {

	// Download as CSV
	$(".export-as-csv").on('click', function (event) {
		// CSV
		// Reconstruction needed because some of the cells are showing up weirdly. D:
		$('.non-csv').hide();
		var tableString = "<table><tr>";

		// Header
		$('th').each(function(){
			if($(this).is(':visible')){
				tableString += "<th>"+$(this).text().trim()+"</th>";
			}
		});
		tableString += "</tr>";

		// Rows
		$('tbody > tr').each(function(){
			// Check if row is visible
			if($(this).is(':visible')){
				tableString += "<tr>";

				// Cells
				$(this).find('td').each(function(){
					if($(this).is(':visible')){
						tableString += "<td>"+$(this).text().trim()+"</td>";
					}
				});

				tableString += "</tr>";
			}
		});

		$('#hidden-table-container').html(tableString);
		$('.non-csv').show();
		exportTableToCSV.apply(this, [$('#hidden-table-container > table'), 'logs.csv']);
		// IF CSV, don't do event.preventDefault() or return false
		// We actually need this to be a typical hyperlink
	});

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

	// asterisk inputbox
	var asterisk = $('.required-invisible-container').html();
	var specialAsterisk = $('.required-invisible-container-rfid-fingerprint').html();
	
	// required
	$('.required').each(function(){
		$(this).wrap('<div class="required-field-block"></div>');
		$(this).after(asterisk);
	});

	// required-rfid-fingerprint
	$('.required-rfid-fingerprint').each(function(){
		$(this).wrap('<div class="required-field-block"></div>');
		$(this).after(specialAsterisk);
	})

	$(function() {
		$('.required-icon').tooltip({
			placement: 'left',
			title: 'Required field'
		});
	});

	$(function() {
		$('.required-icon-rfid-fingerprint').tooltip({
			placement: 'left',
			title: 'A fingerprint template OR an RFID card must be entered.'
		});
	});

	// Editing text
	$(document.body).on('click', '.editable-text', function(){
		if (editableTextTrigger) { // some other text is already being edited; close that first
			$('.editable-done').trigger('click');
			editableTextTrigger = false;
		}
		// we are editing another textbox
		editableTextTrigger = true;

		var newHtml = ''; // the HTML that will replace this element
		var requiredHtml = '';
		var isRfidFingerprint = false;

		var parent = $(this).parent();
		var field = parent.data('field');
		
		// these fields are in the modal
		if (field == 'pin' || field == 'rfid' || field == 'fingerprint' || field == 'name') {
			editedTextInModal = true;
		}

		// generate the textbox that will replace this element
		var currentValue = $(this).html().trim();
		if (currentValue == '- - -') {
			currentValue = ''; // effectively blank
		} else if (field == 'doors' || field == 'keypairs') {
			currentValue = ''; // the textbox should be empty because we will replace it later
		}
		if (field == 'rfid' || field == 'fingerprint') {
			requiredHtml = 'required-rfid-fingerprint';
			isRfidFingerprint = true;
		}
		
		newHtml += '<div class="col-md-8"><input type="text" class="editing-text form-control '+requiredHtml+'" value="' + currentValue + '" /></div>';

		if(isRfidFingerprint){
			var scanButton = '<div class="scan-edit"><span class="glyphicon glyphicon-search"></span></div>';
			newHtml += scanButton;
		}

		var doneButton = '<div class="completed-check editable-done"><span class="glyphicon glyphicon-ok-sign"></span></div>';
		newHtml += doneButton;
		parent.html(newHtml);

		if(isRfidFingerprint){
			// required-rfid-fingerprint
			$('.required-rfid-fingerprint').each(function(){
				$(this).wrap('<div class="required-field-block"></div>');
				$(this).after(specialAsterisk);
			})

			$(function() {
				$('.required-icon-rfid-fingerprint').tooltip({
					placement: 'left',
					title: 'A fingerprint template OR an RFID card must be entered.'
				});
			});
		}

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
		
	}).on('keypress', '#modal-credential-text', function(e){
		if(e.keyCode == 13) {
			$('.modal-authenticate-btn').trigger('click');
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
			var newValue = parent.find('input').val().trim();
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
		var scanUrl = parent.data('scan-url');
		var waitUrl = parent.data('wait-url');

		if(strcmp('#modal-credential-text', target) == 0){ // target is the textbox in authenticate modal
			$(target).attr('type', 'text');
			$('#modal-active-field').val(field);
		}

		if (field == 'rfid') {
			placeholder = 'Please swipe an RFID card.';
		} else if (field == 'fingerprint') {
			placeholder = 'Please put your finger on the scanner.';
		}

		// Clear target textbox and replace with placeholder
		$(target).val('');
		$(target).attr('placeholder', placeholder);

		scanButton.hide(256);
		
		onSuccess = function(msg) {
			scanButton.show(256);
			$(target).val(msg);
			$(target).attr('placeholder', '');
		};
		
		onError = function(msg) {
			// nothing was scanned: show error as textbox placeholder
			scanButton.show(256);
			$(target).attr('placeholder', msg['responseText'])
			// alert(msg['responseText']);
		};

		if (field == 'rfid') {
			postToUrl(scanUrl, {}, onSuccess, onError);
		} else if (field == 'fingerprint') {
			// If the target is 3x, then:
			if(strcmp($('#scan-url-thrice').val(), scanUrl) == 0){
				postToUrl(scanUrl, {'stage' : 1}, function(msg) {
					// scanned the first finger
					$(target).attr('placeholder', 'Please remove your finger from the scanner.');
					postToUrl(waitUrl, {}, function(msg) {
						// finger removed
						$(target).attr('placeholder', 'Please scan the same finger again.');
						postToUrl(scanUrl, {'stage' : 2}, function(msg) {
							// scanned the second finger
							$(target).attr('placeholder', 'Please remove your finger from the scanner.');
							postToUrl(waitUrl, {}, function(msg) {
								// finger removed
								$(target).attr('placeholder', 'Please scan the same finger yet again.');
								postToUrl(scanUrl, {'stage' : 3}, onSuccess, onError);
							}, onError);
						}, onError);
					}, onError);
				}, onError);
			}

			// Else if the target is just 1x then:
			else{
				postToUrl(scanUrl, {}, onSuccess, onError);
			}
		}
	});

	// Keypair Actions
	$(document.body).on('click', '.keypair-activate-btn', function(){
		var btn = $(this);
		btn.html("Loading...");
		postIdToUrlInParent(btn, function(msg) {
			btn.html("Activate");
			var row = btn.closest('tr');
			$('#keypairs-table tbody').append(row);
			row.find('.activated-action').removeClass('invisible');
			row.find('.deactivated-action').addClass('invisible');
		});

	}).on('click', '.keypair-deactivate-btn', function(){
		var btn = $(this);
		btn.html("Loading...");
		postIdToUrlInParent(btn, function(msg) {
			btn.html("Deactivate");
			var row = btn.closest('tr');
			$('#deactivated-keypairs-table tbody').append(row);
			row.find('.activated-action').addClass('invisible');
			row.find('.deactivated-action').removeClass('invisible');
		});

	// User Actions
	}).on('click', '.user-activate-btn', function(){
		var btn = $(this);
		btn.html("Loading...");
		postIdToUrlInParent(btn, function(msg) {
			btn.html("Deactivate");
			btn.removeClass('user-activate-btn activate-btn btn-success');
			btn.addClass('user-deactivate-btn deactivate-btn btn-warning');

			var row = btn.closest('tr');
			row.removeClass('greyed');
		});
	}).on('click', '.user-deactivate-btn', function(){
		var btn = $(this);
		btn.html("Loading...");
		postIdToUrlInParent(btn, function(msg) {
			btn.html("Activate");
			btn.removeClass('user-deactivate-btn deactivate-btn btn-warning');
			btn.addClass('user-activate-btn activate-btn btn-success');

			var row = btn.closest('tr');
			row.addClass('greyed');
		});
	}).on('click', '.delete-btn, .deny-btn', function(){
		var btn = $(this);
		postIdToUrlInParent(btn, function(msg) {
			btn.closest('tr').hide(256);
		});
	}).on('click', '.edit-btn', function(){
		var parent = $(this).parent();
		var id = parent.data('id');

		transformModalIntoAuthenticate(id);

	}).on('click', '.modal-enter-pin', function(){
		var id = $("#authenticate-modal").data('id');
		var name = $('#name-'+id).data('value');

		$('#modal-credential-text').val('');
		$('#modal-credential-text').focus();
		$('#modal-active-field').val('pin');
		$('#modal-credential-text').attr('type', 'password');

	}).on('click', '.modal-authenticate-btn', function(){
		var id = $("#authenticate-modal").data('id');
		var url = $('.credential').data('post-url');

		postToUrl(url, {
			id : id,
			val : $('#modal-credential-text').val(),
			type: $('#modal-active-field').val()
		}, function(msg) {
			transformModalIntoEditKeypair(id, msg);
		}, function(msg) {
			$('.modal-error-credentials').show();
			$('#modal-credential-text').val();
			setTimeout(function() {
				$('.alert').each(function(){
					$(this).fadeOut(500);
				});
			}, 2000);
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


	setTimeout(function() {
		$('.alert').each(function(){
			$(this).fadeOut(500);
		});
	}, 2000);
});


function transformModalIntoAuthenticate(id) {
	var name = $('#name-' + id).data('value').trim();
	var modalTitle = 'Enter any credential of user (' + name + '):';
	$("#authenticate-modal").data('id', id);
	$('#modal-credential-text').attr('placeholder', 'Enter credential.');

	$('#edit-modal > .modal-dialog > .modal-content > .modal-header > .modal-title').html(modalTitle);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body').html($('#authenticate-modal > .body').html());
	$('#edit-modal > .modal-dialog > .modal-content > .modal-footer').html($('#authenticate-modal > .footer').html());

	var hasPin = false;
	var hasRfid = false;
	var hasFingerprint = false;

	var btnPin = $('.modal-footer > span > #btn-modal-pin');
	var btnRfid = $('.modal-footer > span > #btn-modal-rfid');
	var btnFingerprint = $('.modal-footer > span > #btn-modal-fingerprint');

	if(strcmp($('#pin-'+id).text().trim(), "Yes") == 0)
		hasPin = true;
	if(strcmp($('#rfid-'+id).text().trim(), "Yes") == 0)
		hasRfid = true;
	if(strcmp($('#fingerprint-'+id).text().trim(), "Yes") == 0)	
		hasFingerprint = true;

	if (hasRfid) {
		$('#modal-active-field').val('rfid');
		btnRfid.removeAttr('disabled');
	}
	else {
		// user has no rfid credential
		btnRfid.attr('disabled', 'true');
	}
	if (hasFingerprint){
		$('#modal-active-field').val('fingerprint');
		btnFingerprint.removeAttr('disabled');
	}
	else {
		btnFingerprint.attr('disabled', 'true');
	}

	if (hasPin) {
		btnPin.removeAttr('disabled');
		$('.modal-enter-pin').trigger('click');
		$('#modal-credential-text').focus();
		$('#modal-active-field').val('pin');
	}
	else {
		btnPin.attr('disabled', 'true');
	}

}

function transformModalIntoEditKeypair(id, msg){
	var name = $('#name-'+id).data('value').trim();	
	var modalTitle = name + '\'s Credentials';

	var userPIN = msg['pin'];
	var userRFID = msg['rfid_uid'];
	var userFING = msg['fingerprint_template'];

	if(!userPIN){userPIN = '- - -';}
	if(!userRFID){userRFID = '- - -';}
	if(!userFING){userFING = '- - -';}

	$('#edit-modal > .modal-dialog > .modal-content > .modal-header > .modal-title').html(modalTitle);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body').html($('#edit-keypair-modal > .body').html());
	$('#edit-modal > .modal-dialog > .modal-content > .modal-footer').html($('#edit-keypair-modal > .footer').html());

	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-name').data('id', id);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-name > span').html(name);

	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-pin').data('id', id);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-pin > span').html(userPIN);

	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-rfid').data('id', id);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-rfid > span').html(userRFID);

	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-fingerprint').data('id', id);
	$('#edit-modal > .modal-dialog > .modal-content > .modal-body > .edit-fingerprint > span').html(userFING);

}

function getToken() {
	return document.getElementsByName('csrfmiddlewaretoken')[0].value;
}

function postToUrl(postUrl, data, onSuccess, onError) {
	data['csrfmiddlewaretoken'] = getToken();
	onError = onError || function(msg) {
		alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
		location.reload();
	};
	$.ajax({
		type: 'POST',
		url: postUrl,
		data: data,
		success: onSuccess,
		error: onError
	});
}

function postIdToUrlInParent(element, onSuccess, onError) {
	var parent = element.parent();
	var id = parent.data('id');
	var postUrl = parent.data('post-url');
	var val = $(element).val();
	postToUrl(postUrl, {id:id, val:val}, onSuccess, onError);
}

function strcmp ( str1, str2 ) {
	// http://kevin.vanzonneveld.net
	// +   original by: Waldo Malqui Silva
	// +      input by: Steve Hilder
	// +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
	// +    revised by: gorthaur
	// *     example 1: strcmp( 'waldo', 'owald' );
	// *     returns 1: 1
	// *     example 2: strcmp( 'owald', 'waldo' );
	// *     returns 2: -1

	return ( ( str1 == str2 ) ? 0 : ( ( str1 > str2 ) ? 1 : -1 ) );
}

function exportTableToCSV($table, filename) {

	var $rows = $table.find('tr:has(td)'),

	// Temporary delimiter characters unlikely to be typed by keyboard
	// This is to avoid accidentally splitting the actual contents
	tmpColDelim = String.fromCharCode(11), // vertical tab character
	tmpRowDelim = String.fromCharCode(0), // null character

	// actual delimiter characters for CSV format
	colDelim = '","',
	rowDelim = '"\r\n"',

	// Grab text from table into CSV formatted string
	csv = '"' + $rows.map(function (i, row) {
		var $row = $(row),
			$cols = $row.find('td');

		return $cols.map(function (j, col) {
			var $col = $(col),
				text = $col.text();

			return text.replace(/"/g, '""'); // escape double quotes

		}).get().join(tmpColDelim);

	}).get().join(tmpRowDelim)
		.split(tmpRowDelim).join(rowDelim)
		.split(tmpColDelim).join(colDelim) + '"',

	// Data URI
	csvData = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);

	$(this).attr({
	    'download': filename,
        'href': csvData,
        'target': '_blank'
	});
}