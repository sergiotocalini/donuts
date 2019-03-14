function UnpublishedFormatterDate(value, row) {
    html = moment(Date.parse(value)).format("YYYY-MM-DD HH:mm");
    html+= "<span class='pull-right'>";
    html+= " <i class='fa fa-fw fa-calendar' title='" + moment(Date.parse(value)).fromNow() + "'></i>";
    html+= "</span>";
    return html
};

function UnpublishedFormatterAction(value, row) {
    var html = '';
    if ( row.action == 'Add' ) {
	html+='<i class="fa fa-fw fa-plus-square text-success"></i>'
    } else if ( row.action == 'Edit' ) {
	html+='<i class="fa fa-fw fa-pen-square text-warning"></i>';
    } else if ( row.action == 'Del') {
	html+='<i class="fa fa-fw fa-minus-square text-danger"></i>';
    } else {
	html+='<i class="fa fa-fw fa-info-circle"></i>';
    }
    return html;
};

function UnpublishedFormatterMaster(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function UnpublishedFormatterView(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function UnpublishedFormatterZone(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function UnpublishedFormatterName(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function UnpublishedFormatterOwner(value, row) {
    var html = ""
    html += '<img class="fa fa-fw img-circle" src="';
    html += row.owner.avatar + '"/> ';
    html += row.owner.displayname;
    return html;
};

function UnpublishedFormatterActions(value, row) {
    var html = '';
    html += '<a href="#publish" data-click="publish" data-id="' + row.id + '">';
    html += ' <i class="fa fa-arrow-up"></i>';
    html += '</a>';
    html += '<a href="#delete" data-click="delete" data-id="' + row.id + '">';
    html += ' <i class="fa fa-trash"></i>';
    html += '</a>';
    return html;
};

function UnpublishedParams(params) {
    return params
};

function UnpublishedResponseHandler(res) {
    var data = [];
    for(r in res.data) {
    	var row = res.data[r];
    	data.push({
    	    name: row.name,
	    view: row.view,
    	    date: row.created_on,
	    owner: row.user,
	    master: row.master,
	    zone: row.zone,
	    id: row._id,
	    action: row.action,
    	});
    };
    return data;
};

function UnpublishedActions(action, id) {
    var table = "#table-unpublished";
    var url = null;
    if (action == 'delete') {
	url = "{{ url_for('publish_remove') }}?id=" + id;
    } else if (action == 'publish') {
	url = "{{ url_for('publish_this') }}?id=" + id;
    }

    if (url !== null) {
	console.log(url);
	$.ajax({
	    url: url,
	    type: 'GET',
	    contentType: "application/json",
	    success: function(e) {
		$(table).bootstrapTable('remove', {'field': 'id', 'values': [id] });
	    }
	});
    }    
}

function jqlisteners() {
    $('#table-unpublished a[data-click=publish]').unbind();
    $('#table-unpublished a[data-click=publish]').click(function(e) {
	e.preventDefault();
	UnpublishedActions('publish', $(this).data('id'))
    });
    $('#table-unpublished a[data-click=delete]').unbind();
    $('#table-unpublished a[data-click=delete]').click(function(e) {
	e.preventDefault();
	UnpublishedActions('delete', $(this).data('id'))
    });
};

$(document).ready(function() {
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
    $("#toolbar-unpublished button[data-click=publish-bulk]").on("click", function(a) {
	a.preventDefault();
	var table = "#table-unpublished";
	var selected = $(table).bootstrapTable('getAllSelections');
	if ( selected.length > 0 ) {
	    var confirm = "Are you sure you want to publish <strong>" + selected.length  + " items</strong> ?";
	    bootbox.confirm(confirm, function(result) {
		if (result == true) {
		    for (s in selected) {
			UnpublishedActions('publish', selected[s]['id'])
		    }
		};
	    });
	};
    });
    $("#toolbar-unpublished button[data-click=delete-bulk]").on("click", function(a) {
	a.preventDefault();
	var table = "#table-unpublished";
	var selected = $(table).bootstrapTable('getAllSelections');
	if ( selected.length > 0 ) {
	    var confirm = "Are you sure you want to delete <strong>" + selected.length  + " items</strong> ?";
	    bootbox.confirm(confirm, function(result) {
		if (result == true) {
		    for (s in selected) {
			UnpublishedActions('delete', selected[s]['id'])
		    }
		};
	    });
	};
    });    
});
