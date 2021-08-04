$(document).ready(function(){
	$('#nav-icon1').click(function(){
		$(this).toggleClass('open');
		$(".admin-nav-block").toggleClass("close");
	});
});