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

	$('#newDoors').tokenInput('/doors/search/', {
		theme: 'facebook',
		hintText: 'Type a door name...',
		prePopulate: null,
		preventDuplicates : true
	});
});


// $(window).bind('beforeunload', function(){
// 	return 'Are you sure you want to leave?';
// });

// For editing text
$(document).ready(function() {
	var editableTextTrigger = false;

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
		// generate the textbox that will replace this element
		var currentValue = $(this).html().trim();
		if (currentValue == '- - -') {
			currentValue = ''; // effectively blank
		} else if (field == 'doors') {
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

		if (field == 'doors') {
			// replace the textbox with tokenInput
			var kid = parent.data('id');
			var doors = eval(parent.data('value'));
			var searchUrl = parent.data('search-url');

			$('.editing-text').tokenInput(searchUrl, {
				theme: 'facebook',
				hintText: null,
				prePopulate: doors,
				preventDuplicates : true,
				onAdd: function(door) {
					postUrl = parent.data('link-url');
					postToUrl(postUrl, {kid:kid, did:door.id})
				},
				onDelete: function(door) {
					postUrl = parent.data('unlink-url');
					postToUrl(postUrl, {kid:kid, did:door.id})
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

		if (field == 'doors') {
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
			// send changes to server
			var id = parent.data('id');
			var postUrl = parent.data('post-url');
			postToUrl(postUrl, {id:id, value:newValue});
		}
		newHtml += '</span>';	
		parent.html(newHtml);

		editableTextTrigger = false;
		// $('.editing-text').off('click');

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
		postIdToUrlInParent($(this));

		$(this).closest('tr').removeClass('greyed'); // ungrey the corresponding row
		$(this).addClass('deactivate-btn btn-warning').removeClass('activate-btn btn-success');
		$(this).html("Deactivate");

	}).on('click', '.deactivate-btn', function(){
		postIdToUrlInParent($(this));

		$(this).closest('tr').addClass('greyed'); // grey out the corresponding row
		$(this).removeClass('deactivate-btn btn-warning').addClass('activate-btn btn-success');
		$(this).html("Activate");

	}).on('click', '.delete-btn, .deny-btn', function(){
		postIdToUrlInParent($(this));

		$(this).closest('tr').hide(256);
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
				// need to update buttons and the number of unapproved users in the navbar
				location.reload()
			},
			error: function(msg){
				alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
				location.reload();
			}
		});

	}).on('click', '.demote-btn', function(){
		postIdToUrlInParent($(this));

		var id = $(this).parent().data('id');
		$('#star-' + id).hide();
		$(this).removeClass('demote-btn btn-warning').addClass('promote-btn btn-success');
		$(this).html("Promote");

	}).on('click', '.promote-btn', function(){
		postIdToUrlInParent($(this));

		var id = $(this).parent().data('id');
		$('#star-' + id).show();
		$(this).addClass('demote-btn btn-warning').removeClass('promote-btn btn-success');
		$(this).html("Demote");
	});
});

function getToken() {
	return document.getElementsByName('csrfmiddlewaretoken')[0].value;
}

function postToUrl(postUrl, data) {
	data['csrfmiddlewaretoken'] = getToken();
	$.ajax({
		type: 'POST',
		url: postUrl,
		data: data,
		success: function(msg){
		},
		error: function(msg){
			alert('Whoops, looks like something went wrong... \n Message: '+msg['responseText']+'\n Refreshing...');
			location.reload();
		}
	});
}

function postIdToUrlInParent(element) {
	var parent = element.parent();
	var id = parent.data('id');
	var postUrl = parent.data('post-url');
	postToUrl(postUrl, {id:id});
}