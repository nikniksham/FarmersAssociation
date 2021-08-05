$('[name^=contentPage]').click(function(){
    var num = parseInt(this.name.match(/\d+/))
    console.log(num)
    $('#contentPage'+num).toggleClass('visible')
})