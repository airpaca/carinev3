var m=""
function build_poll_menu(){
    $.ajax({
        url: '{% url "get_poll_menu"  %}',
        async : true,
        success : function(msg){
            m=msg
            $('#poll-menu').append(m)
        }
    });   
}
function switch_poll(p){
    $('.table-container').children().remove()
    $.ajax({
        url: '{% url "get_table_fine"  %}',
        data : {
            poll : p
        },
        async : true,
        success : function(msg){
            m=msg
            $('.table-container').append(m)
        }
    });  
}
$('.table-fine').css('height',$(window.height))
function show_img(url){
    window.open(url)
}
function toggle_active(id){
    $.ajax({
        url: '{% url "set_fine_active"  %}',
        data : {
            id : id
        },
        async : true,
        success : function(msg){
        }
    });  
}

build_poll_menu()