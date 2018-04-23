function toggle_active(ctx_id){
    url = '{% url "set_ctx" %}'
    
    $.ajax({
        url:url,
        data : {
            ctx_id : ctx_id
           
        },
        success(msg){
            console.log(msg)
            $('#tools-nav-bar').text('Paramètres actifs : ' + msg['active'])
        }
    })
    
}
