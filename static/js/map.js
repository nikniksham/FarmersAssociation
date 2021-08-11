ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
        center: [55.751574, 37.573856],
        zoom: 9
    }, {
        searchControlProvider: 'yandex#search'
    })

    // Создаём макет содержимого.
    MyIconContentLayout = ymaps.templateLayoutFactory.createClass(
        '<div style="color: #FFFFFF; font-weight: bold;" onclick="console.log(' + "'click'" + ')">$[properties.iconContent]</div>'
    )

    myPlacemark = new ymaps.Placemark(myMap.getCenter(), {
        hintContent: 'Riogas',
        balloonContent: 'Riogas<br>Эко-ферма<br>роды деятельности<br><a href="tel+81112223344">+8(111) 222-33-44</a><br>main-riogas@mail.com<br><a href="/">на берлин</a>'
    }, {
        // Опции.
        // Необходимо указать данный тип макета.
        iconLayout: 'default#image',
        // Своё изображение иконки метки.
        iconImageHref: 'static/img/partner-1.jpg',
        // Размеры метки.
        iconImageSize: [50, 50],
        // Смещение левого верхнего угла иконки относительно
        // её "ножки" (точки привязки).
        iconImageOffset: [-25, -25]
    })

    myPlacemark.events.add('click', function () {
        console.log('О, событие!');
    });

    myMap.geoObjects
        .add(myPlacemark)
        .add(myPlacemarkWithContent);
});