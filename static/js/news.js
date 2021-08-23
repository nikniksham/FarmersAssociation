var loaded_news = 9
var load_news = 9
var link_website = ""
var search_text = ""
var delete_load_button = false

function add_news() {
    var req = link_website+"api/newspage/"+loaded_news+"/"+(loaded_news + load_news);
    if (search_text !== "") {
        req += "/"+search_text
    }
    $.get( req, function( data ) {
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
            console.log(document.getElementsByClassName("more-news")[0])
            document.getElementsByClassName("more-news")[0].innerHTML = ''
            console.log(document.getElementsByClassName("more-news")[0])
            delete_load_button = true
        } else if (delete_load_button) {
            console.log("add")
            document.getElementsByClassName("more-news")[0].innerHTML = '<a class="load-news" onclick="add_news()"><button>Больше новостей</button></a>'
            delete_load_button = false
        }
    });
}

function searching_text() {
    search_text = document.getElementsByClassName("findtext")[0].value;
    document.getElementById("news").innerHTML = ""
    loaded_news = 0
    add_news()
}