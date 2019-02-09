function HistoryFormatterDate(value, row) {
    html = moment(Date.parse(value)).format("YYYY-MM-DD HH:mm");
    html+= "<span class='pull-right'>";
    html+= " <i class='fa fa-fw fa-calendar' title='" + moment(Date.parse(value)).fromNow() + "'></i>";
    html+= "</span>";
    return html
};

function HistoryFormatterAction(value, row) {
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

function HistoryFormatterMaster(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function HistoryFormatterView(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function HistoryFormatterZone(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function HistoryFormatterName(value, row) {
    var html = '';
    if ( typeof value !== 'undefined' && value !== null ) {
	html += value;
    }
    return html;
};

function HistoryFormatterOwner(value, row) {
    var html = ""
    html += '<img class="fa fa-fw img-circle" src="';
    html += row.owner.avatar + '"/> ';
    html += row.owner.displayname;
    return html;
};

function HistoryFormatterActions(value, row) {
    var html = '';
    html += "<a class='history-log' href='#history-open' data-log='" + row.out + "'>";
    html += " <i class='fa fa-fw fa-file'></i>";
    html += "</a>";
    return html;
};

function HistoryParams(params) {
    return params
};

function HistoryResponseHandler(res) {
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
	    out: row.out
    	});
    };
    return data;
};

function jqlisteners() {
    jqlisteners_history_modal_log();
};

$(document).ready(function() {
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
});
