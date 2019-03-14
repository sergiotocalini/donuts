function AdminUsersFormatterDisplay(value, row) {
    var html = "";
    html+='<span>';
    html+=' <img src="' + row.avatar + '" class="fa fa-fw img-circle"/>';
    html+=' <span>' + value + '</span>';
    html+='</span>';
    if (! row.status) {
	html += '<i style="margin:0.1%" class="fa fa-fw fa-user-slash pull-right"></i>';
    }
    if (row.admin) {
	html += '<i style="margin:0.1%" class="fa fa-fw fa-user-shield pull-right"></i>';
    }
    return html;
};

function AdminUsersFormatterCreatedOn(value, row) {
    if ( typeof value !== 'undefined' && value !== null ) {
	return moment(Date.parse(value)).fromNow();
    }
    return 'Never'
};

function AdminUsersFormatterLastSeen(value, row) {
    if ( typeof value !== 'undefined' && value !== null ) {
	return moment(Date.parse(value)).fromNow();
    }
    return 'Never'
};

function AdminUsersFormatterActions(value, row) {
    var html = ""
    html += '<a class="user-open" data-toggle="confirmation" ';
    html += 'data-id="' + row.id + '" href="#">';
    html += '<i class="fa fa-fw fa-search"></i>';
    html += '</a>';
    html += '<a class="user-del" data-toggle="confirmation" ';
    html += 'data-id="' + row.id + '" href="#">';
    html += '<i class="fa fa-fw fa-trash"></i>';
    html += '</a>';
    return html;
}

function AdminUsersParams(params) {
    params = {};
    return params
};

function AdminUsersResponseHandler(res) {
    var data = [];
    for(r in res.data) {
    	var row = res.data[r];
    	data.push({
	    id: row._id,
	    userid: row.id,
	    email: row.email,
	    avatar: row.avatar,
	    last_sync: row.last_update,
	    display: row.displayname,
	    admin: row.admin,
	    status: row.active,
	    expiration: row.expirations,
    	});
    };
    return data;
};

function jqlisteners() {
    console.log('jqlisteners - admin/users/index.js');
    $('.change-admin-privs').click(function(event) {
	var user_id = $(this).parent().parent().attr('id');
	console.log(user_id);
	bootbox.confirm("Are you sure you want to change this permissions?", function(result) {
	    if (result == true){
		changeAdminPrivs(user_id); 
	    } else {
		
	    }
	}); 
	event.preventDefault();
    });
    $('.change-active').click(function(event) {
	var user_id = $(this).parent().parent().attr('id');
	bootbox.confirm("Are you sure you want to change user status?", function(result) {
	    if (result == true){
		changeUserStatus(user_id); 
	    }else{
		
	    }
	}); 
	event.preventDefault();
    });
    $('.change-expiration').click(function(e) {
	e.preventDefault();
	var user_id = $(this).parent().parent().attr('id');
	bootbox.confirm("Are you sure you want to change user expirations privs?", function(result) {
	    if (result == true){
		changeUserExpirations(user_id); 
	    }
	});
    });
};

$(document).ready(function() {
    $(window).resize(function () {
	autosize_tables();
    });
    autosize_tables();
});
