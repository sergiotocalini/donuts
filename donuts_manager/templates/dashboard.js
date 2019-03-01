$(document).ready(function() {
    var chart = c3.generate({
	bindto: '#domain_exp_pie',
	data: {
	    // iris data from R
	    columns: [
		['Yes', {{ctx.exp_counter}}],
		['No', {{ctx.no_exp_counter}}],
	    ],
	    type : 'pie',
	    onclick: function (d, i) { console.log("onclick", d, i); },
	    onmouseover: function (d, i) { console.log("onmouseover", d, i); },
	    onmouseout: function (d, i) { console.log("onmouseout", d, i); }
	}
    });

    var chart = c3.generate({
	bindto: '#published_pie',
	data: {
	    // iris data from R
	    columns: [
		{% for p in ctx.published %}
		['{{p.0}}', {{p.1}}],
		{% endfor %}
	    ],
	    type : 'pie',
	    onclick: function (d, i) { console.log("onclick", d, i); },
	    onmouseover: function (d, i) { console.log("onmouseover", d, i); },
	    onmouseout: function (d, i) { console.log("onmouseout", d, i); }
	}
    });
});
