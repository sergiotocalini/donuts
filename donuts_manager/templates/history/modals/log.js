
function jqlisteners_history_modal_log() {
    $(".history-log").unbind();
    $(".history-log").click(function(e) {
	e.preventDefault();
	var modal = "#ModalHistoryLog";
	$(modal).find('#history-log-terminal').html('<pre>' + $(this).data('log') + '</pre>');
	$(modal).modal('show');
    });
};
