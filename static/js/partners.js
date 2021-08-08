var speedPartners = 2000

function openPopUp(name) {
    $('#'+name).toggleClass('visible');
}

$(document).ready(function(){
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
});