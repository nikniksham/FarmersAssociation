var speedPartners = 2000
var speedPartnerImageCarousel = 2000
var deltaX = 0

function openPopUp(name) {
    if (Math.abs(deltaX) <= 10) {
        $('#'+name).toggleClass('visible');
        $('.carousel').slick('refresh');
        if ($('#'+name).hasClass("visible")) {
            $("body").addClass("stop-scroll-2");
        } else if (!$('#'+name).hasClass("visible")) {
            $("body").removeClass("stop-scroll-2");
        }
    }
    deltaX = 0
}

$(document).ready(function(){
    $('.partner-image-carousel').slick({
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedCarousel,
        slidesToShow: 1,
        draggable: true,
        arrows: false,
        swipeToSlide: true,
    });

    $('.partners-carousel').slick({
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedPartners,
        slidesToShow: 4,
        draggable: true,
        arrows: false,
        swipeToSlide: true,
        responsive: [
            {
              breakpoint: 768,
              settings: {
                autoplay: false,
                slidesToShow: 1
              }
            },
            {
              breakpoint: 991,
              settings: {
                slidesToShow: 2
              }
            },
            {
              breakpoint: 1200,
              settings: {
                slidesToShow: 3
              }
            },
            {
              breakpoint: 1300,
              settings: {
                slidesToShow: 4
              }
            }
        ]
    });

    $('.partner-item').mousedown(function(event) {
        deltaX = event.pageX
    });
    $('.partner-item').mouseup(function(event) {
        deltaX -= event.pageX
    });
});