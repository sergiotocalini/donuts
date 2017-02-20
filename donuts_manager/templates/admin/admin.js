
function changeAdminPrivs(user_id){
    var url = "{{url_for('change_privs')}}?user_id="+user_id;
    callUrlAndReload(url);
}

function changeUserStatus(user_id){
    var url = "{{url_for('change_status')}}?user_id="+user_id;
    callUrlAndReload(url);
}

function changeUserExpirations(user_id){
    var url = "{{url_for('change_expirations')}}?user_id="+user_id;
    callUrlAndReload(url);
}