var loaded_news = 9
var load_news = 9
var link_website = "http://127.0.0.1:8000/"

function add_news() {
    $.get( link_website+"api/newspage/"+loaded_news+"/"+(loaded_news + load_news), function( data ) {
        console.log(data);
        console.log(loaded_news+"/"+(loaded_news + load_news));
        loaded_news += load_news
        for (var i=0; i < data.length; i++) {
            let block = document.createElement('div');
            block.className = "col-sm-12 col-md-6 col-lg-4";
            block.innerHTML = "<a href='/news-page/"+data[i].link+"'><div class='news'><div class='news-img' style='background-image: url(/static/img/"+data[i].image.split('//')[0]+");'></div><div class='news-title'>"+data[i].heading+"</div><div class='news-text'>"+data[i].mini_text+"</div><div class='news-navigation'><span class='date'>"+data[i].created_date+"</span></div></div></a>"
            document.getElementById("news").append(block)
        }
        if (data.length < load_news) {
            $('.more-news').remove()
        }
    });
}