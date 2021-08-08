var speedHeadCarousel = 1000
var speedCarousel = 1000

$(document).ready(function(){
    $('.carousel').slick({
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedCarousel,
        slidesToShow: 1,
        draggable: true,
        arrows: false,
        swipeToSlide: true,
    });
});