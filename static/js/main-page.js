$(document).ready(function(){
    $('#nav-icon2').click(function(){
        $(this).toggleClass('open');
        $(".navigation").toggleClass("visible");
        if ($(".navigation").hasClass("visible")) {
            $("body").addClass("stop-scroll-1");
        } else if (!$(".navigation").hasClass("visible")) {
            $("body").removeClass("stop-scroll-1");
        }
    });

    $(function() {
        $(window).scroll(function() {
            if($(this).scrollTop() > 1600) {
                $('#toTop').fadeIn();
            } else {
                $('#toTop').fadeOut();
            }
        });
        $('#toTop').click(function() {
            $('body,html').animate({scrollTop:0},800);
        });
    });
});