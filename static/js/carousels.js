$(document).ready(function(){
    $('.main-news-carousel').slick({
      dots: false,
      accessibility: false,
      infinite: true,
      speed: 500,
      autoplay: boolAutoplay,
      autoplaySpeed: speedNews,
      fade: true,
      cssEase: 'linear',
      arrows: false
    });

    $('.partners-carousel').slick({
        dots: false,
        infinite: true,
        autoplay: boolAutoplay,
        autoplaySpeed: speedPartners,
        slidesToShow: 5,
        variableWidth: true,
        draggable: true,
        arrows: false,
        centerMode: true,
        swipeToSlide: true,
        responsive: [
            {
              breakpoint: 768,
              settings: {
                autoplay: false
              }
            }
        ]
    });
});