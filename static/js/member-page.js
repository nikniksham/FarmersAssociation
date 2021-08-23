$(document).ready(function(){
    $('.carousel-members-for').slick({
      slidesToShow: 1,
      slidesToScroll: 1,
      arrows: false,
      fade: true,
      asNavFor: '.carousel-members'
    });

    $('.carousel-members').slick({
      slidesToShow: 4,
      slidesToScroll: 1,
      asNavFor: '.carousel-members-for',
      centerMode: true,
      focusOnSelect: true
    });
});