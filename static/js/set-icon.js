function readIconURL(input) {
    if (input.files && input.files[0]) {
        var num = parseInt(input.id.match(/\d+/))
        var fr = new FileReader();
        fr.onload = function () {
            $('#'+input.name).attr('src', fr.result);
            if ($('#'+input.name).attr('class') === 'this-is-image') {
                $('#'+input.name).toggleClass("visible");
            }
        }
        fr.readAsDataURL(input.files[0]);
    }
}


$("body").delegate('[id^="iconInput"]', "change", function(){
    readIconURL(this)
})