function sendEditRecord(event){
    $('.alert').addClass('hide');
    var form = $('#EditRecordForm');
    var url = "{{ url_for('edit_record') }}?";
    var data = $(form).serialize();
    console.log(data);
    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
	data: data,
        success: function(request){
            $('#EditRecordModal').modal('hide');
            // showZone(ZONE);
        },
        error: function(request){
            for (k in request['responseJSON']['errors']){
                var key = request['responseJSON']['errors'][k][0];
                showError(key);
            }   
        }
    });
};

function expirationForm(zone){
    var url = '{{url_for('zone_expiration')}}?';
    url += 'zone=' + zone;
    $.get(url, function(data){
        console.log(data);
        $('#expirationModalBody').html(data);
                $('#expirationModal').modal('show');
    });
};

function delZone(zone, view){
    bootbox.confirm("Are you sure you want to remove the zone?", function(result) {
        if (result == true){
            loading();
            $.ajax({
		url: "{{ url_for('remove_zone') }}",
		type: "GET",
		data: { zone: zone, view: view},
		success: function(request){
		    var url = "{{url_for('zones_list')}}";
                    //window.location.replace(url);
		},
		error: function(request){
		}
            });
        }
    }); 
};

function actionsFormatter(value, row){
    var html = "";
    html+='<a class="record-edit" href="#record-edit" data-name="' + row.name + '"';
    html+='   data-zone="' + row.zone + '" data-ttl="' + row.ttl + '"';
    html+='   data-value="' + row.value + '" data-view="' + row.view + '"';
    html+='   data-type="' + row.type + '">';
    html+=' <i class="fa fa-pencil"></i>';
    html+='</a>'
    html+='<a class="record-del" href="#record-del" data-name="' + row.name + '"';
    html+='   data-zone="' + row.zone + '" data-ttl="' + row.ttl + '"';
    html+='   data-value="' + row.value + '" data-view="' + row.view + '"';
    html+='   data-type="' + row.type + '">';
    html+=' <i class="fa fa-trash"></i>';
    html+='</a>';
    return html;
};

function ZoneParams(params) {
    params = {};
    params['zone'] = "{{ ctx.zone }}";
    params['view'] = "{{ ctx.view }}";
    return params
};

function ZoneResponseHandler(res) {
    var data = [];
    for(r in res.records) {
    	var row = res.records[r];
    	data.push({
    	    name: row.name,
	    type: row.type,
    	    value: row.value,
	    ttl: row.ttl,
	    zone: "{{ ctx.zone }}",
	    view: "{{ ctx.view }}"
    	});
    };
    return data;
};

function jqlisteners() {
    $("#expiration-btn").unbind();
    $('#expiration-btn').click(function(event){
	var zone = $(this).data('zoneid');
	expirationForm(zone)
    })
    $(".delZone").unbind();
    $(".delZone").click(function(e) {
	e.preventDefault();
	delZone($(this).data('zone'), $(this).data('view'));
    });
    $(".record-edit").unbind();
    $(".record-edit").click(function(e) {
	e.preventDefault();
        var zone = $(this).data('zone');
	var view = $(this).data('view');
        var name = $(this).data('name');
        var type = $(this).data('type');
        var value = $(this).data('value');
        var ttl = $(this).data('ttl');
	$('#EditRecordModalZoneName').html('Edit Record to ' + zone);
	$('#EditRecordForm').html('');
	$('#EditRecordForm').html($('.EditRecordForm').html());
	$('#EditRecordForm').find('#name').val(name);
	$('#EditRecordForm').find('#ttl').val(ttl);
	$('#EditRecordForm').find('#value').val(value);
	$('#EditRecordForm').find('#name_original').val(name);
	$('#EditRecordForm').find('#ttl_original').val(ttl);
	$('#EditRecordForm').find('#value_original').val(value);
	$('#EditRecordForm').find('#zone').val(zone);
	$('#EditRecordForm').find('#view').val(view);
	$('#EditRecordForm').find('#type_original').val(type);
	$('#EditRecordForm').find('#type').val(type);
	$('#EditRecordModal').modal('show');
	$('#btnEditRecord').on('click', function(event){
            event.preventDefault();
            sendEditRecord(event);
	});
    });
    $(".record-del").unbind();
    $(".record-del").click(function(e) {
	e.preventDefault();
        var zone = $(this).data('zone');
	var view = $(this).data('view');
        var name = $(this).data('name');
        var type = $(this).data('type');
        var value = $(this).data('value');
        var ttl = $(this).data('ttl');
	bootbox.confirm("Are you sure you want to remove the record?", function(result) {
	    if (result == true) {
		$.ajax({
		    url: "{{ url_for('remove_record') }}",
		    type: "POST",
		    data: {
			'ttl': ttl, 'type': type, 'zone': zone,
			'value': value, 'name': name, 'view': view,
		    },
		    dataType: "json",
		    success: function(request){
			console.log(request)
			// var url = "{{ url_for('zone_page', zone='zone-name') }}";
			// url = url.replace('zone-name', zone);
		    },
		    error: function(request){
		    }
		});	 
	    }
	}); 
    });
};

$(document).ready(function() {
    $("#record-add").unbind();
    $("#record-add").click(function(e) {
	e.preventDefault();
	var modal = "#ModalRecord";
	var display = "Add record to " + $(this).data('zone');
	$(modal).find('.modal-title').html(display);
	$(modal).find('#record-master').val($(this).data('master'));
	$(modal).find('#record-view').val($(this).data('view'));
	$(modal).find('#record-zone').val($(this).data('zone'));
	$(modal).find('#record-zone-span').html($(this).data('zone'));
	$(modal).find('#record-name').val();
	$(modal).find('#record-type').selectpicker('val', 'A');
	$(modal).find('#record-ttl').val(1800);
	$(modal).find('#record-value').val();
	$(modal).find('#record-note').val();
	$(modal).modal('show');
    });
    $("#record-save").unbind();    
    $("#record-save").on('click', function(e){
	e.preventDefault();
	var modal = "#ModalRecord";
	var table = "#table-zone"
	var form = $(modal).find('form');
	var data = {};
	$(form).serializeArray().map(function(x){data[x.name.replace('record-', '')] = x.value;});
	$.ajax({
    	    url: "{{ url_for('add_record') }}",
    	    type: "POST",
    	    data: data,
    	    dataType: "json",
    	    success: function(request){
		$(table).bootstrapTable('refresh');
		$(modal).modal('hide');
    	    },
    	    error: function(request){
    		for (k in request['responseJSON']['errors']){
    		    var key = request['responseJSON']['errors'][k][0];
    		    showError(key);
    		}	
    	    }
	});
    });
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
});
