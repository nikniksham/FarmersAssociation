var speedHeadCarousel = 1000

$(document).ready(function(){
    $('.header-carousel').slick({
        accessibility: false,
        speed: 500,
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedHeadCarousel,
        slidesToShow: 1,
        draggable: false,
        arrows: false,
        fade: true,
        cssEase: 'linear'
    });
});