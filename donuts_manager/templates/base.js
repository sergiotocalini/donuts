function autosize_tables(selected) {
    if ( selected == null || selected === '' ) {
	var tables = $('body').find(".table-autosize");
    } else {
	var tables = $('body').find(selected);
    }
    tables.each(function(row){
	var selector = $(tables[row]).attr('id');
	selector = '#' + selector;
	$(selector).on('post-body.bs.table', function () {
	    jqlisteners();
	});
	$(selector).bootstrapTable({
	    height: table_height(selector),
	});
	$(selector).bootstrapTable('resetView', {
	    height: table_height(selector),
	});
    });
};

function table_height(table) {
    var parent = $(table).parent().parent().parent().parent();
    return parent.height();
};

function select_loader_agents_masters(sel, option) {
    $(sel).prop('disabled', true);
    $.ajax({
	async: true,
	type: "GET",
	url: "{{ url_for('api_admin_agents') }}",
	data: { type: 'Master' },
	success: function (e) {
	    $(sel).html("");
	    for(agent in e['data']) {
		var row = e['data'][agent];
		html ='<option value="' + row['_id'] + '" ';
		html+='data-tokens="' + row['name'] + '" ';
		html+='data-icon="fa fa-fw fa-cube" ';
		html+='data-subtext="' + row['ip'] + '">';
		html+=row['name'];
		html+='</option>';
		$(sel).append(html);
	    }
	    $(sel).prop('disabled', false);
	    $(sel).selectpicker('refresh');
	},
    });
};

function select_loader_agents_views(sel, master) {
    $(sel).prop('disabled', true);
    $(sel).html("");

    var views = ['public', 'private']
    for(v in views) {
	html ='<option value="' + views[v] + '" ';
	html+='data-tokens="' + views[v] + '" ';
	html+='data-icon="fa fa-fw fa-eye" ';
	html+='data-subtext="">';
	html+=views[v];
	html+='</option>';
	$(sel).append(html);	
    }
    
    $(sel).prop('disabled', false);
    $(sel).selectpicker('refresh');
};

ALL_ZONES = [];
function getZones() {
    $.ajax({
	async: false,
	type: 'GET',
	xhrFields: {
	    withCredentials: true
	},
	url: "{{ url_for('show_zones') }}",
	success: function(data) {
	    for (x in data['data']['zones']){
		var n = data['data']['zones'][x]['zone'];
		data['data']['zones'][x]['name'] = n;
	    }
	    ALL_ZONES = data['data']['zones'];
	},	    
    });  
};

function loading() { 
    $('#loading').modal('show');
    $('#loading').find('.modal-content').css('background-color','transparent');
};

function loadingDone(){
    $('#loading').modal('hide');
};

function goToZone(zone){
    {% if ctx.app_name == 'index' %}
    showZone(zone);
    {% else %}
    var url = '{{url_for('zones_list')}}?zone=' + zone;
    window.location.replace(url);
    {% endif %}	
};

function autoSearch(){
    if (ALL_ZONES.length == 0){
	getZones();
    }
    var $input = $('#search');
    $input.typeahead({'source': ALL_ZONES}).change(function(){
	var current = $input.typeahead("getActive");
	var zone = current['name'];
	goToZone(zone);
    });
}

$.extend({
    redirectPost: function(location, args) {
        var form = '';
        $.each( args, function( key, value ) {
            form += '<input type="hidden" name="'+key+'" value="'+value+'">';
        });
        $('<form action="'+location+'" method="POST">'+form+'</form>').appendTo('body').submit();
    }
});

function addZone(){
    $('#AddZoneModal').modal('show');
};

function loggedIn(){
    console.log('check logged in');
    $.ajax({async: false,
	    type: 'GET',
	    xhrFields: {
		withCredentials: true
	    },
	    url: "{{ url_for('logged_in') }}",
	    success: function(data) {
		setTimeout(loggedIn, 20000)		
	    },
	    error: function(request){
		console.log(request);
	    }
    });;  
};

function callUrlAndReload(url){
    $.ajax({
        url: url,
        type: "GET",
        dataType: "json",
        success: function(request){
            location.reload();
        },
        error: function(request){
            location.reload();      
        }
    });
};

function showError(key){
    var tmp = '#'+key+'_error';
    $('#EditRecordModal').find(tmp).removeClass('hide');
    $('#AddRecordModal').find(tmp).removeClass('hide');
    setTimeout(function(){
            $('#EditRecordModal').find(tmp).addClass('hide');
            $('#AddRecordModal').find(tmp).addClass('hide');
	
    }, 3000);
};

$(document).ready(function() {
    $("#addZone").click(function() {
	addZone();
    });
    autoSearch();
    loggedIn();
    $(document).on("click", "[data-click=main-sidebar-toggle]", function(e) {
	e.preventDefault();
	$('.sidebar').toggleClass("toggled");
	$('.header-bar').toggleClass("toggled");
	$('.wrapper').toggleClass("toggled");
	$('.footer-bar').toggleClass("toggled");
	$('.table').bootstrapTable('resetView');
    });
});

if (!String.prototype.format) {
    String.prototype.format = function() {
        var str = this.toString();
        if (!arguments.length)
            return str;
        var args = typeof arguments[0],
            args = (("string" == args || "number" == args) ? arguments : arguments[0]);
        for (arg in args)
            str = str.replace(RegExp("\\{" + arg + "\\}", "gi"), args[arg]);
        return str;
    }
};
