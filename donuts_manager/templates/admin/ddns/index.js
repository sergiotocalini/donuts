function AdminDDNSFormatterLastSync(value, row) {
    if ( typeof value !== 'undefined' && value !== null ) {
	return moment(Date.parse(value)).fromNow();
    }
    return 'Never'
};

function AdminDDNSFormatterOwner(value, row) {
    return value;
};

function AdminDDNSFormatterActions(value, row) {
    var html = "";
    html+='<a class="ddns-del" href="#ddns-del" data-click="ddns-del" data-id="' + row.id + '">';
    html+=' <i class="fa fa-trash"></i>'
    html+='</a>'    
    return html;
};

function AdminDDNSParams(params) {
    params = {};
    return params
};

function AdminDDNSResponseHandler(res) {
    var data = [];
    for(r in res.data) {
    	var row = res.data[r];
    	data.push({
	    id: row._id,
	    ip: row.ip,
	    last_sync: row.last_update,
	    hash: row.hash,
    	    name: row.ddns,
	    owner: row.user_email,
    	});
    };
    return data;
};

function AdminDDNSActions(action, id) {
    var table = "#table-admin-ddns";
    var method = 'GET';
    var data = {};
    if (action == 'del') {
	method = 'DELETE';
    }

    $.ajax({
	url: "{{ url_for('api_admin_ddns') }}?id=" + id,
	type: method,
	data: data,
	contentType: "application/json",
	success: function(e) {
	    $(table).bootstrapTable('remove', {'field': 'id', 'values': [id] });
	}
    });
}

function jqlisteners() {
    $("#table-admin-ddns a[data-click=ddns-del]").unbind();
    $("#table-admin-ddns a[data-click=ddns-del]").click(function(e) {
	e.preventDefault();
       	AdminDDNSActions('del', $(this).data('id'));
    });    
}

$(document).ready(function() {	
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
    $("#ddns-add").click(function(e) {
	e.preventDefault();
	$('#ModalDDNS').modal('show');
    });
    $("#toolbar-admin-ddns button[data-click=ddns-del-bulk]").on("click", function(a) {
	a.preventDefault();
	var table = "#table-admin-ddns";
	var selected = $(table).bootstrapTable('getAllSelections');
	if ( selected.length > 0 ) {
	    var confirm = "Are you sure you want to delete <strong>" + selected.length  + " items</strong> ?";
	    bootbox.confirm(confirm, function(result) {
		if (result == true) {
		    for (s in selected) {
			AdminDDNSActions('del', selected[s]['id'])
		    }
		};
	    });
	};
    });    
});
