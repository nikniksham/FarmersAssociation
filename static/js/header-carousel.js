var speedHeadCarousel = 6750

$(document).ready(function() {
    $('.header-carousel').slick({
        accessibility: false,
        speed: 0,
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedHeadCarousel,
        slidesToShow: 1,
        draggable: false,
        arrows: false,
        fade: true,
        cssEase: 'ease',
        pauseOnHover: false
    });

    $('.header-carousel-text').slick({
        accessibility: false,
        speed: 500,
        dots: false,
        infinite: true,
        autoplay: true,
        autoplaySpeed: speedHeadCarousel - 500,
        slidesToShow: 1,
        draggable: false,
        arrows: false,
        fade: true,
        cssEase: 'ease',
        pauseOnHover: false
    });

    $('.header-carousel').on('beforeChange', function(event, slick, currentSlide, nextSlide){
        console.log("change src");
        var images = $(".need-change");
        console.log(images);
        $('.header-carousel').slick('slickGoTo', nextSlide);
        for (var i=0; i < images.length; i++) {
          $(images[i]).attr('src', $(images[i]).attr('src'));
        }
    });
});