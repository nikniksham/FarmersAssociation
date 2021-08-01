var count_images = 1



function addImage(num) {
    document.getElementById("images"+num).innerHTML += '<div class="input-file-row-1"><div class="upload-file-container"><div class="delete-image"></div><img id="image'+count_images+'" class="this-is-image" src="#" alt=""/><input type="file" name="image'+count_images+'" class="photo" id="imgInput'+count_images+'"/></div></div>'
    count_images += 1;
    $('[id^="imgInput"]').change(function(){
        console.log('loadImage');
        readURL(this);
    });

    $('[id^="imgInput"]').each(function(){
        count_images += 1;
    });

    $('[id^="addImage"]').click(function() {
        console.log('add');
        var num = parseInt(this.id.match(/\d+/))
        addImage(num);
    });

    $('.delete-image').click(function(){
        console.log('delete');
        var father = $(this).closest('.input-file-row-1');
        var src = $($(father.children()[0]).children()[1]).attr('src');
        if (src === undefined || src === '' || src === '#') {
            console.log('no i don"t delet')
        } else {
            console.log('delete')
            $(this).closest('.input-file-row-1').remove();
        }
    });
}

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        var num = parseInt(input.id.match(/\d+/))
        console.log(num);
        reader.onload = function (e) {
            $('#image'+num).attr('src', e.target.result);
            if ($('#image'+num).attr('class') === 'this-is-image') {
                addImage(parseInt($($($(input).closest('.settings-images')).children()[0]).attr('id').match(/\d+/)));
                $('#image'+num).toggleClass("visible");
                $(this).closest('.upload-file-container').toggleClass('un-visible');
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}


$(document).ready(function(){
    $('[id^="imgInput"]').change(function(){
        console.log('loadImage');
        readURL(this);
    });

    $('[id^="imgInput"]').each(function(){
        count_images += 1;
    });

    $('[id^="addImage"]').click(function() {
        console.log('add');
        var num = parseInt(this.id.match(/\d+/))
        addImage(num);
    });

    $('.delete-image').click(function(){
        console.log('delete');
        var father = $(this).closest('.input-file-row-1');
        var src = $($(father.children()[0]).children()[1]).attr('src');
        if (src === undefined || src === '' || src === '#') {
            console.log('no i don"t delet')
        } else {
            console.log('delete')
            $(this).closest('.input-file-row-1').remove();
        }
    });
});