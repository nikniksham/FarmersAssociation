var speedCarousel = 2000

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