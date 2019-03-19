var zones = {{ctx.zones|tojson|safe}};
console.log(zones);	
var user_id = '{{ctx.user.id}}';

$( document ).ready(function() {
    $("#admin" ).change(function() {
	changeAdminPrivs(user_id); 
  	return false;
    });
    var $input = $('#search-zone');
    $input.typeahead({'source': zones}).change(function(){
	var current = $input.typeahead("getActive");
	zone = current['name'];
	var url = "{{url_for('edit_user_zones')}}?action=add&user_id="+user_id;
	url += '&zone=' + zone;
   	callUrlAndReload(url);	
    });
    $('.change-admin-privs').click(function(event){
	event.preventDefault();
	var url = $(this).attr('href');	
	bootbox.confirm("Are you sure you want to change this permissions?", function(result) {
	    if (result == true){
		callUrlAndReload(url);	
	    }else{

	    }
	}); 
    });
    $(".del-zone" ).click(function() {
	var zone = $(this).parent().parent().attr('id');	
	bootbox.confirm("Are you sure you want to delete this zone?", function(result) {
	    if (result == true){

	  	var url = "{{url_for('edit_user_zones')}}?action=del&user_id="+user_id;
		url += '&zone=' + zone;
		callUrlAndReload(url);	
	    }else{

	    }
	}); 

    });
});

