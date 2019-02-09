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
    html += '<a href="#publish" data-id="' + row.id + '">';
    html += ' <i class="fa fa-arrow-up"></i>';
    html += '</a>';
    html += '<a href="#delete" data-id="' + row.id + '">';
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
    	    date: row.published_datetime,
	    owner: row.user,
	    master: row.master,
	    zone: row.zone,
	    id: row._id,
	    action: row.action,
    	});
    };
    return data;
};

function jqlisteners() {
    console.log('entro');
};

$(document).ready(function() {
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
});
