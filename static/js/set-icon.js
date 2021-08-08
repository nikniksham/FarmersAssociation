function readIconURL(input) {
    if (input.files && input.files[0]) {
        var num = parseInt(input.id.match(/\d+/))
        var fr = new FileReader();
        fr.onload = function () {
            $('#icon').attr('src', fr.result);
            if ($('#icon').attr('class') === 'this-is-image') {
                $('#icon').toggleClass("visible");
                $($($('#icon').closest('.upload-file-container')[0]).children()[0]).toggleClass("hidden");
            }
        }
        fr.readAsDataURL(input.files[0]);
    }
}


$("body").delegate('[id^="iconInput"]', "change", function(){
    readIconURL(this)
})