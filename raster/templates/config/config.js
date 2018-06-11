var ctx_active_tmp;
function toggle_active(){
    ctx_id = ctx_active_tmp
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
    hideConfirmValidContexte()
    
}
function confirmValidContexte(ctx_id){
    ctx_active_tmp=ctx_id
	$('#mask').show()
	$('#confirm-contexte-div').show()
}
function hideConfirmValidContexte(){
	$('#mask').hide()
	$('#confirm-contexte-div').hide()
}
function show_ctx_info(ctx_id){
    $("#ctx-info-container").children().remove()
    ctx_ob=get_ctx_info(ctx_id)

}
function get_ctx_info(id_ctx){
    
    $.ajax({
        url : '{% url "get_ctx_info" %}',
        data: { id_ctx : id_ctx },
        success : function (msg){
            console.log(msg)
            tbl=build_ctx_info_table(msg)
                
            $("#ctx-info-container").append(tbl) 
            btn='<div type="button"  onclick=confirmValidContexte('+id_ctx.toString()+') class="div-valid">Activer le contexte <br></br></div>'
            $("#ctx-info-container").append(btn) 
        }
    })
}
function build_ctx_info_table(ctx_ob){
    html='<table class="table table-striped"><thead></thead><tbody><tr>'
    html+='<th>nom du contexte :</th><td>' + ctx_ob.nom + '</td></tr>'
    html+='<tr><th>actif : </th><td>'+ctx_ob.active+'</td></tr>'
    html+='<tr><th>export site web : </th><td>'+ctx_ob.webprod+'</td></tr>'
    html+='<tr><th>export site preprod : </th><td>'+ctx_ob.webpreprod+'</td></tr>'
    html+='<tr><th>adresse de la base utilisée : </th><td>'+ctx_ob.bdd+'</td></tr>'
    html+='<tr><th>activation du module fine échelle : </th><td>'+ctx_ob.fine+'</td></tr>'
    html+='</tbody></table>'    
    return html    
}