var speedHeadCarousel = 6000

$(document).ready(function() {
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
        cssEase: 'linear',
        pauseOnHover: false
    });

    $('.header-carousel').on('beforeChange', function(event, slick, currentSlide, nextSlide){
        console.log("change src");
        $(".need-change").attr('src', $(".need-change").attr('src'));
    });
});