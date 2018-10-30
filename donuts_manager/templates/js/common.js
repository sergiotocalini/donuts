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
}
function table_height(table) {
    var parent = $(table).parent().parent().parent().parent();
    return parent.height();
};
