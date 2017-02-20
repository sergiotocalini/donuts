function addRecord(zone){
    $('#AddRecordModalZoneName').html('Add Record to ' + zone);
    $('.ZoneNameTag').html(zone);
    $('#AddRecordForm').html('');
    $('#AddRecordForm').html($('.AddRecordFormTemplate').html());
    $('#AddRecordForm').find('#zone_id').val(zone);
    $('#AddRecordModal').modal('show');
    $( "#btnAddRecord" ).unbind();
    $('#btnAddRecord').on('click', function(event){
	event.preventDefault();
	sendAddRecord(event);
    });
    $('#AddRecordForm').find('#record_type').change(function(){
        var rtype = $(this).val();
        if (rtype === 'MX'){
            $('#record-input').hide();
        }else{
            $('#record-input').show();
        }
    })
}


function sendAddRecord(event){
    $('.alert').addClass('hide');
    var form = $('#AddRecordModal').find('form');
    var url = "{{url_for('add_record')}}";
    var data = {};
    $(form).serializeArray().map(function(x){data[x.name] = x.value;});

    $.ajax({
	url: url,
	type: "POST",
	data: data,
	dataType: "json",
	success: function(request){
	    hideAddRecordModal();
	    var url = "{{url_for('zone_page', zone='zone-name')}}";
	    url = url.replace('zone-name', value);
	    window.location.replace(url);
    	},
	error: function(request){
	    for (k in request['responseJSON']['errors']){
		var key = request['responseJSON']['errors'][k][0];
		showError(key);
	    }	
	}
    });
}


function hideAddRecordModal(){
    $('#AddRecordModal').modal('hide');
}

function showError(key){
    var tmp = '#'+key+'_error';
    $('#EditRecordModal').find(tmp).removeClass('hide');
    $('#AddRecordModal').find(tmp).removeClass('hide');
    setTimeout(function(){
            $('#EditRecordModal').find(tmp).addClass('hide');
            $('#AddRecordModal').find(tmp).addClass('hide');
	
    }, 3000);
}
