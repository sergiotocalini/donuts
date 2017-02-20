ALL_ZONES = [];
function getZones(){
    $.ajax({async: false,
	    type: 'GET',
	    xhrFields: {
		withCredentials: true
	    },
	    url: '{{url_for('show_zones')}}',
	    success: function(data) {
		for (x in data['data']['zones']){
		    var n = data['data']['zones'][x]['zone'];
		    data['data']['zones'][x]['name'] = n;
		}
		ALL_ZONES = data['data']['zones'];
	    },

	   });;  
}
function loading(){
    
    $('#loading').modal('show');
    $('#loading').find('.modal-content').css('background-color','transparent');
}
function loadingDone(){
    $('#loading').modal('hide');
}

function goToZone(zone){
	{% if ctx.app_name == 'index' %}
	    showZone(zone);
	{% else %}
		var url = '{{url_for('zones_list')}}?zone=' + zone;
		window.location.replace(url);
	{% endif %}
	
}
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
$.extend(
{
    redirectPost: function(location, args)
    {
        var form = '';
        $.each( args, function( key, value ) {
            form += '<input type="hidden" name="'+key+'" value="'+value+'">';
        });
        $('<form action="'+location+'" method="POST">'+form+'</form>').appendTo('body').submit();
    }
});
function addZone(){
    $('#AddZoneModal').modal('show');

} 
$( document ).ready(function() {
    $("#addZone").click(function() {

        addZone();
    });
    $("#addZoneForm").submit(function(event){
      $('#AddZoneModal').modal('hide');
      loading();
      var url = "{{url_for('add_zone')}}?";
      url += $(this).serialize();
      $.ajax({
          url: url,
          type: "GET",
          success: function(data){
              loadingDone();
	      window.location.reload();
	  }
      });
      event.preventDefault();
    });
    autoSearch();
    loggedIn();

});


function loggedIn(){
    console.log('check logged in');
    $.ajax({async: false,
	    type: 'GET',
	    xhrFields: {
		withCredentials: true
	    },
	    url: '{{url_for('logged_in')}}',
	    success: function(data) {
		setTimeout(loggedIn, 20000)		
	    },
	    error: function(request){
		console.log(request);
	    }
    });;  
}
