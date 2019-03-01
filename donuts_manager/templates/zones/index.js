function ZonesFormatterName(value, row) {
    var url = "{{ url_for('zone_page', zone='zone-name') }}" + "?view=" + row.view;
    url = url.replace('zone-name', value);

    var html = '';
    html+= '<span>';
    html+= ' <a href="' + url + '" > ' + value + '</a>';
    html+= '</span>';
    html+= '<span class="pull-right">';
    if (row.unpublished > 0) {
	html+= ' <span class="badge badge-success">';
	html+=  row.unpublished;
	html+= ' </span>'
    }
    html+= '</span>';
    return html;
};

function ZonesFormatterActions(value, row) {
    html ='<a class="zone-open" data-toggle="confirmation" ';
    html+='   data-view="' + row.view + '" data-zone="' + row.name + '"';
    html+='   data-container="body" href="#zone-open">';
    html+=' <i class="fa fa-fw fa-search"></i>';
    html+='</a>';
    html+='<a class="zone-delete" data-toggle="confirmation" ';
    html+='   data-view="' + row.view + '" data-zone="' + row.name + '"';
    html+='   data-container="body" href="#zone-delete">';
    html+=' <i class="fa fa-fw fa-trash"></i>';
    html+='</a>';
    return html;
};

function ZonesParams(params) {
    return params
};

function ZonesResponseHandler(res) {
    var data = [];
    for(r in res.data.zones) {
    	var row = res.data.zones[r];
    	data.push({
    	    name: row.name,
	    view: row.view,
    	    unpublished: row.to_publish,
	    owner: row.owner,
    	});
    };
    console.log(data);
    return data;
};

function jqlisteners() {
    console.log();
};

$(document).ready(function() {	
    $("#toolbar-zones button[data-click=zone-add]").on("click", function(a) {
	a.preventDefault();
	$('#ModalZone').modal('show');
    });

    $('#btnCloseRecord').on('click', function(event){
	hideAddRecordModal();
	// refreshZones();
	autosize_tables();
	event.preventDefault();
    });
    // autoSearch();
    $("select[id=agents-masters]").on('loaded.bs.select', function(e) {
	select_loader_agents_masters($(this));
    });
    $("select[id=agents-masters]").on('changed.bs.select', function(e) {
	select_loader_agents_views('#agents-views', $(this).val());
    });
    $("#zone-save").unbind();
    $("#zone-save").click(function(e) {
	e.preventDefault();
	var modal = '#ModalZone';
	var form = {
	    master: $(modal).find('#agents-masters').val(),
	    view: $(modal).find('#agents-views').val(),
	    zone: $(modal).find('#zone').val(),
	}
	console.log(form);
	$.ajax({
            url: "{{ url_for('add_zone') }}",
            type: "GET",
	    data: form,
            success: function(data) {
		console.log(data);
		$(modal).modal('hide');
	    },
	    error: function(data) {
		console.log(data);
	    }
	});
    });    
    autosize_tables();
});
