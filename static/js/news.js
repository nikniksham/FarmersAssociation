var loaded_news = 9
var load_news = 9

function add_news() {
    $.get( "{{link_website}}/api/newspage/"+loaded_news+"/"+(loaded_news + load_news), function( data ) {
        console.log(data);
        console.log(loaded_news+"/"+(loaded_news + load_news));
        loaded_news += load_news

    });
}