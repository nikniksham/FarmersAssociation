var count_images = 1
var max_count = 15


function addImage(num) {
    if count_images > max_count:
        return
    let block = document.createElement('div');
    block.className = "input-file-row-1";
    block.innerHTML = '<div class="upload-file-container"><div class="delete-image"></div><img id="image'+count_images+'" class="this-is-image" src="#" alt=""/><input type="file" name="image'+count_images+'" class="photo" id="imgInput'+count_images+'"/></div>';
    document.getElementById("images"+num).append(block);
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

    $('.delete-image').click(function() {
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
        var num = parseInt(input.id.match(/\d+/))
        var fr = new FileReader();
        console.log(1)
        fr.onload = function () {
            console.log(2)
            $('#image'+num).attr('src', fr.result);
            console.log(3)
            if ($('#image'+num).attr('class') === 'this-is-image') {
                addImage(parseInt($($($(input).closest('.settings-images')).children()[0]).attr('id').match(/\d+/)));
                $('#image'+num).toggleClass("visible");
            }
        }
        fr.readAsDataURL(input.files[0]);
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