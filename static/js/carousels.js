$(document).ready(function(){
    $('.main-news-carousel').slick({
      dots: false,
      accessibility: false,
      infinite: true,
      speed: 500,
      autoplay: boolAutoplay,
      autoplaySpeed: speedNews,
      fade: true,
      cssEase: 'linear'
    });
    $('.partners-carousel').slick({
        dots: false,
        infinite: true,
        autoplay: boolAutoplay,
        autoplaySpeed: speedPartners,
        slidesToShow: 5,
        variableWidth: true,
        responsive: [
            {
              breakpoint: 769,
              settings: {
                autoplay: false
              }
            }
        ]
    });
});