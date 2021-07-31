last = "SEO"

function readURL(input, num) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#image'+num).attr('src', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

$("#imgInput1").change(function(){
    readURL(this, 1);
});
$("#imgInput2").change(function(){
    readURL(this, 2);
});
$("#imgInput3").change(function(){
    readURL(this, 3);
});

function changeScreen(input) {
    $("#"+last).toggleClass("visible");
    $("#"+input.name).toggleClass("visible");
    last = input.name
}

$(".admin-nav").click(function(){
    changeScreen(this);
});