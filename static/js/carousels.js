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
      arrows: false,
    });

    $('.partners-carousel').slick({
        dots: false,
        infinite: true,
        autoplay: boolAutoplay,
        autoplaySpeed: speedPartners,
        slidesToShow: 5,
        draggable: true,
        arrows: false,
        swipeToSlide: true,
        responsive: [
            {
              breakpoint: 768,
              settings: {
                autoplay: false,
                slidesToShow: 2
              }
            },
            {
              breakpoint: 541,
              settings: {
                slidesToShow: 1
              }
            },
            {
              breakpoint: 769,
              settings: {
                slidesToShow: 2
              }
            },
            {
              breakpoint: 1025,
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
});