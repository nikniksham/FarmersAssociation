var myMap;

ymaps.ready(function () {
    myMap = new ymaps.Map('map', {
        center: [55.751574, 37.573856],
        zoom: 9
    }, {
        searchControlProvider: 'yandex#search'
    })

    // Создаём макет содержимого.
    MyIconContentLayout = ymaps.templateLayoutFactory.createClass(
        '<div style="color: #FFFFFF; font-weight: bold;" onclick="console.log(' + "'click'" + ')">$[properties.iconContent]</div>'
    )

    update_map();
});