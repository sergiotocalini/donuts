function nameFormatter(value, row) {
    var url = "{{ url_for('zone_page', zone='zone-name') }}" + "?view=" + row.view;
    url = url.replace('zone-name', value);
    var link = '<a href="' + url + '" > ' + value + '</a>';
    return link;
}

function actionsFormatter(value, row) {
    var html = '<a href="#" class="addRecord" data-zoneid="';
    html += value;
    html +='"><i class="fa fa-plus"/></a>';
    return html;
}

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
    	    published: row.to_publish,
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
    // refreshZones();
    $(".Showzonesmain").click(function() {
	// refreshZones();
	autosize_tables();
    });

    $('#btnCloseRecord').on('click', function(event){
	hideAddRecordModal();
	// refreshZones();
	autosize_tables();
	event.preventDefault();
    });
    // autoSearch();

    $('#btnAddRecord').on('click', function(event){
	event.preventDefault();
	sendAddRecord(event);
    });
    autosize_tables();
});
