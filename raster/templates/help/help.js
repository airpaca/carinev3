function show_FAQ(){
    $("#content").children().hide()
    $("#faq_div").show()
}

$('.question_div').click( function() {
    
    $(this).find('.question_content_div').toggle()

    })