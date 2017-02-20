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
}

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

}
