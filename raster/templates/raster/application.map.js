{% load static %}
/*riables globales pour stocker les paramtres de correction */
var corr_pollutant = "";
var corr_echeance = "";
var corr_type = "";
var corr_coords = [];
var corr_value = "";

var lib_ech=["j-1","j+0","j+1","j+2"]
var polls={}
var echs={}

var process_files=false
var calc_multi=false
$.ajax({
    url: '{% url "init_dallefine" %}',
    async : true
});
$.ajax({
    url: '{% url "getTsp" %}',
    async : false,
    success : function(msg){
        today=msg['t']
        yesterday=msg['y']
        yyesterday=msg['yy']
    }
});
function format_date(tsp){
    d=new Date(tsp*1000)
    console.log(d)
    y=d.getFullYear()

    m=d.getMonth()+1
    d=d.getDate()
    str = d.toString() +'/' + m.toString() + '/' + y.toString()
    return str
}
function format_date_ymd(tsp){
    d=new Date(tsp*1000)
    console.log(d)
    y=d.getFullYear()

    m=d.getMonth()+1
    d=d.getDate()
    str = y.toString() +  m.toString().padStart(2,"0") + d.toString().padStart(2,'0')
    return str
}
console.log(today,yesterday,yyesterday)
var runs={}
runs[today]=0
runs[yesterday]=1
runs[yyesterday]=2

// init des dates de j0  j-2 pour afficher dans le tableau de droite

var jp0 = 'Auj'
var jm1 = 'Hier'
var jm2 = 'Av-Hier'
console.log(jp0,jm1,jm2)
var dumb=0;
var stats={};
var ic={};
var drawLayer;
/* Creation de la carte */
var map = L.map('map', { zoomControl:false }, {layers: []}).setView([45, 5.0], 8);    
map.attributionControl.addAttribution('CARINE v3 &copy; ATMO Aura - 2017</a>'); 

/*2eme frame*/
var map2 = L.map('map2', { zoomControl:false }, {layers: []}).setView([45, 5.0], 8);    
map2.attributionControl.addAttribution(' CARINE v3 - ATMO Aura - 2017</a>'); 

L.control.scale().addTo(map);

//navigation simultanee sur les deux maps
//TODO : fonctionne mal, a revoir
function onMapMove(e){
    map2.panTo(map.getCenter())
}
function onMapZoom(e){
    map2.setZoom(map.getZoom())
}

/* activation de la navigation simultanee clench?ar clic dans le menu */
function toggleNav(){
    console.log('toggleNav triggered')

    if (map._events.move.length >1 ){
        console.log('remove')
        map._events.zoom.pop()
        map._events.move.pop()
    }
    else {
        map.on('zoom',onMapZoom)
        map.on('move',onMapMove)
    }

}

/* gestionnaire de couches */
//couche active du map-block1
var activeLayer1;
//couche active du map-block2
var activeLayer2;
//TODO : check obsolete?
var baseLayers = {
};
//dict des sources du map-block1
var overlayLayers1 = {
};
//dict des sources du map-block2
var overlayLayers2 = {
};
//dict de toutes les couches vecteurs
var vectorLayers = {    
}
//dict de l'ensemble de ssources retourn? par la vue 'source_url' (redondant overlayersX ? ?oire)
var liste_sources;
var prevs;
var active_poll_right_table;
var active_poll_left
///// --- init ----
function check_statut() {
    $.ajax({
        url: '{% url "check_statut" %}',
        async : false,
        success : function(msg){
            //j=JSON.parse(msg)
            console.log(msg)
            liste_sources=msg;
        }
    });
}

check_statut() 
$.ajax({    
    url: '{% url "get_init_info"  %}',
    async: false,
    success : function(msg){
        //j=JSON.parse(msg)

        var k=Object.keys(msg)
        prevs=msg;
        buildLeftMenu()
        buildRightMenu()
        // preprocess_files()
    }
})    
/*         //construction du menu de droite
        //defaut sur PM10 adaptstat
        //reconstruit ?haque clic sur 
        var dic = getTypeDic('PM10','ada');
        buildTable(dic) */
function update_source(id_prev,id){
    id_but='lay_btn_'+id_prev.toString()
    overlayLayers1[id_but]=id
    $.ajax({
        url: '{% url "update_source"  %}',
        async : false,
        data : {
            id_prev : id_prev,
            id : id
        },
        success : function(msg){
            //console.log(msg)
        }
    });   
    var col;  
    if (liste_sources[id].statut==true){        
        col='green'
    }
    else {
        col='red'
    }
    $("#"+id_but + " > .badge").css('background-color',col)
    var url='{% url "img_multi" %}'

}
/* --------- DEBUT MAP-BLOCK1 ---------- */
/* Fonction de creation du menu de gestion des couches */
function buildLeftMenu() {
        //init sur PM10 ada
    for (i in prevs) {
        if (typeof i === undefined){
            console.log("i => undefined")
        }
        else {
            var pol=prevs[i][0]
            if ($('#'+pol.toLowerCase()+'_switch_1').length<1){
                $('#poll_switch_1').append('<a id="'+pol.toLowerCase()+'_switch_1" class="btn btn-default '+pol+'"> <i></i>'+pol+'</sub> </a>')
                init_switch_1(pol)
                //console.log(pol)
                
            }
        }
    }
    var rll=$('#sidemenu > .raster-menu-left')
    /*for (i in prevs) {
        if (typeof i === undefined){
            console.log("i => undefined")
        }
        else {
            var cls=prevs[i][0].toLowerCase()
            if (cls!='multi'){
                var poll_block = '<div class="list-group point-list-view '+cls+'" id="'+cls+'"></div><div class="divider10"></div>'
                if ($('#'+cls).length<1){
                    rll.append(poll_block)
                }
            }
        }
    }   */
/*     for (i in prevs) {
        if (typeof i === undefined){
            console.log('prev undifed')
        }
        else {
            var cls=prevs[i][0].toLowerCase()
            if (cls!='multi'){
                id_but='lay_btn_'+i.toString()
            var html_btn='<a href="#" class="list-group-item point-item baselayer"  id="'+id_but+'"> <h4 class="list-group-item-heading" >'+cls+'</h4>J ' + prevs[i][1].toString()+ '    <span class="glyphicon glyphicon-chevron-right hide"></span><span class="badge">Ready</span></a>'           
            var sel='#sidemenu > .raster-menu-left > .' + cls
            $(sel).append(html_btn)
            overlayLayers1[id_but]={}
            }
        }
    }   */ 
     $("#poll_switch_1 > .NO2").click()

}
function init_switch_1(poll) {
    //console.log(poll)
     ref="#poll_switch_1 > ."+ poll
     
     $("#poll_switch_1 > ."+ poll).click(           
        function(){
            $("#poll_switch_1 > .active").removeClass('active')
            $("#poll_switch_1 > ."+ poll).addClass('active')
            active_poll_left_table=poll;
            var sel='#sidemenu > .raster-menu-left '
            $("#left-raster-group").remove()
            $(sel).append("<div id='left-raster-group'></div>")
            for (p in prevs) {
                pol = prevs[p][0]
                ech = prevs[p][1]
                if (pol==poll){
                    //console.log(p)
                    //console.log(pol)
                    //console.log(ech)

                    id_but='lay_btn_'+p.toString()
                    cls=pol
                    var html_btn='<a href="#" class="list-group-item point-item baselayer"  id="'+id_but+'"> <h4 class="list-group-item-heading" >'+cls+'</h4>J ' + ech.toString()+ '    <span class="glyphicon glyphicon-chevron-right hide"></span><span class="badge">Ready</span></a>'           
                    $("#left-raster-group").append(html_btn)
                    //overlayLayers1[id_but]={}

                }
            }
            check_sources()
            layer_but_clic()
            divider='<div class="divider10"></div>'
            var sel='#sidemenu > .raster-menu-left '
            $("#left-raster-group").append(divider)
            
        }
    )  
};
function check_sources () {
    $.ajax({
        url: '{% url "check_sources"  %}',
        success : function(msg){
            //j=JSON.parse(msg)
            //console.log(msg)
            //les cles du dic 'liste_source' sont l'id de la source
            var k=Object.keys(msg)
            //on parse chaque source
            for (i=0;i<k.length;i++) {
                //construction du menu de gauche (du map-block1)
                var id_prev=k[i]
                var id=msg[id_prev] 
                update_source(id_prev,id)
            }
        }
    });
}
preprocess_files()
/* function build_left_menu(msg) {
    
    //les cles du dic 'liste_source' sont l'id de la source
    var k=Object.keys(msg)
    //on parse chaque source
    for (i=0;i<k.length;i++) {
        //construction du menu de gauche (du map-block1)
        var ind=k[i]
        var ob=msg[ind]

        if (ob.is_source==true){


            overlayLayers1[id_but]={'id_source' :  ind , 'obj' : ob}
            var sel='#sidemenu > .' + cls
            $(sel).append(html_btn)
            
            if (ob.statut!=true){
                $("#"+id_but + "  > .badge").css("background-color","red")
            }
        }
    }
    layer_but_clic()
} */
/* Fonction de gestion du clic sur les couches */
function layer_but_clic() {

    $('.baselayer').click( function() {
            console.log("clic baselayer")
            $(this).next().removeClass('hide');
			$(".table-corr").remove()
            $(".div-fine").remove()
			$("#table-legend").remove()
            /* Gestion de la liste des couches */       
            // Boutons actifs
            $(this).addClass('active').siblings().removeClass('active');  
            
            if ($(this).closest('div').attr('id') == "no2"){
                $("#pm10 a").removeClass('active');
                $("#o3 a").removeClass('active');
            };
            if ($(this).closest('div').attr('id') == "pm10"){
                $("#no2 a").removeClass('active');
                $("#o3 a").removeClass('active');
            };
            if ($(this).closest('div').attr('id') == "o3"){
                $("#no2 a").removeClass('active');
                $("#pm10 a").removeClass('active');
            };          
            // Chevrons
            $("a .glyphicon-chevron-right").addClass('hide');       
            $("#" + $(this)[0].id + " .glyphicon-chevron-right").removeClass('hide');

            /* Gestion de l'affichage des couches */        
            // Suppression des couches actives
            // condition pour traiter les 2 map-block s?r?nt
            if ($(this).closest("#map-block1").length == 1) {
                id_but=$(this)[0].id
                id_prev=id_but.split('_')[2]
                id_source=overlayLayers1[id_but]
				pol=prevs[id_prev][0]
				
                if (!($('#fine-btn-'+id_prev.toString()).length)){

					$(this).after('<div class="div-fine" id="fine-btn-'+id_prev.toString()+'" onclick="merge_mi_fine('+id_prev+','+id_source+')"><button class="btn btn-secondary btn-fine"><i>Fine échelle</i></button></div>')
					$(this).after('<div class="div-fine" id="exp-btn"><button  onclick="expMenu('+id_source+')" class="btn btn-secondary btn-fine"><i>Corrections</i></button></div>')
                    $(this).after('<div class="div-fine" id="stats-btn-'+id_prev.toString()+'"><button  onclick="statsShow('+id_prev+')" class="btn btn-secondary btn-fine"><i>Stats reg.</i></button><button  onclick="get_stats_reg_unique('+id_prev+')" class="btn btn-secondary btn-fine refresh-stats-btn"> <i class="glyphicon glyphicon-refresh"></i></button></div>')
					$(this).after('<table id="table-legend"><tbody></tbody></table>')
					$.ajax({
							//recup de scoins de la carte necessaires pour que leaflet affiche le png
							url:'{% url "get_legend" %}',
							async:false,
							data : {
								pol : pol
							},
							success : function(msg){

								$("#table-legend > tbody ").append(msg)
							}
						})
				  }
                console.log('id_but_prev : ' + id_but.toString())
                //null si on a pas encore initialis?inutile si on affiche un polluant par defaut)
                switch_map_1(id_but)
                
            }
    });
};

function switch_map_1(id_but){
    
    if ( activeLayer1 != null) {
        map.removeLayer(activeLayer1[1])
        console.log(activeLayer1[1])
    }
    id_source = overlayLayers1[id_but]
    
    console.log('id_source : ' + id_source.toString())
    //workaround pour faire passer la variable id ds l'url

    url_bbox='{% url "bbox_raster" %}'

    img=img_raster_url(id_source)



    // s1="'{% "
    // s2=" %}'"
    // s3=s1 + s + s2
    // console.log(s1 + s + s2)
    $.ajax({
        //recup de scoins de la carte necessaires pour que leaflet affiche le png
        url: url_bbox,
        data : {
            id:id_source
        },
        success : function(msg){
            anchors = [
                [msg['ymax'], msg['xmin']], //haut gauche
                [msg['ymax'], msg['xmax']], //haut droite
                [msg['ymin'], msg['xmax']], //bas droite
                [msg['ymin'], msg['xmin']]  //bas gauche
            ];
            //console.log(anchors)
            lay = L.imageTransform(img, anchors, {opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});     
            lay.addTo(map)
            activeLayer1=[id_source,lay];
            
            //console.log(id_source.toString())
            var tbl=meta_source_tbl(liste_sources[id_source])
            $('#active_layer_div1 > table').remove()
            $('#active_layer_div1').append(tbl)
        }
    }) 
}
/* ---------- FIN MAP-BLOCK1 ------------ */


/* ------ DEBUT MAP-BLOCK2 ------ */
function buildRightMenu(){

    //init sur PM10 ada
    for (i in prevs) {
        if (typeof i === undefined){
            console.log("i => undefined")
        }
        else {
            var pol=prevs[i][0]
            if ($('#'+pol.toLowerCase()+'_switch').length<1){
                $('#poll_switch_2').append('<a id="'+pol.toLowerCase()+'_switch" class="btn btn-default '+pol+'"> <i></i>'+pol+'</sub> </a>')
                init_switch_2(pol)
                $("#poll_switch_2 > .NO2").addClass('active')
            }
        }
    }
    dic=getTypeDic('NO2','ada')
    buildTable(dic)    
    active_poll_right_table="NO2";
}
function getTypeDic(poll,type){

    //reformate le liste source en un dictionnaire facilement utilisable pour construire le tableau
    //chaque ech (supporte pas les id negatif)
    var type_dic={0:{},1:{},2:{},3:{}};
    for (s in liste_sources) {      
        var obj=liste_sources[s]
        if ((obj.type==type) && (obj['pol']==poll) && (obj['intrun']==0)){
            // console.log(obj)
            var ech=obj['ech']+1
            var tsp=obj['daterun']
            //console.log(tsp)

            run=runs[tsp]
            // console.log(run)
            // console.log(obj['pol'])
            //console.log(run)
            type_dic[ech][run]=s;           
        }
    }
    // console.log(type_dic)
    return type_dic;
}
function buildTable(type_dic){
    //TODO : a mettre dynamique selon  les polluants echeances etc.. (pas urgent ceci dit..)
    $(".t2 > thead").remove()
    $(".t2 > tbody").remove()
    $(".t2").append("<thead class='thead-inverse'><tr><th></th><th>"+jm2+"</th><th>"+jm1+"</th><th>"+jp0+"</th><tr></thead>")
    $(".t2").append("<tbody></tbody>")
    for (i in type_dic){
        $(".t2 > tbody").append("<tr id='tr_"+i.toString()+"'><th scope='row'>"+(i-1).toString()+"</th></tr>")
        // console.log(i)
        for (run in type_dic[i]){
            //console.log(run)
            // console.log(run)
            // pour inverser l'ordre des colonnes du tableaux :
            var reverse_ind =(run-2)*(-1)
            //console.log(reverse_ind)
            // console.log(type_dic)
            var id_source=0
            id_source=type_dic[i][reverse_ind]
            
            var col;  
            
            if (liste_sources[id_source].statut==true){        
                col='green'
            }
            else {
                col='red'
            }
            var is_source='not_source'
            for (id_but in overlayLayers1){
                //console.log(overlayLayers1[id_but]['id_source'])
                if (overlayLayers1[id_but]==id_source){
                    is_source='yes_source'  
                }
            }
            $("#tr_" + i.toString()).append("<td class='"+col+" "+is_source+"' id=run_"+id_source+"></td>")
        }   
    }
    td_clic()
}

//on reconstruit le tableau de gestion des couches si on change de polluant
function init_switch_2(poll) {
     ref="#poll_switch_2 > ."+ poll
     $("#poll_switch_2 > ."+ poll).click(           
        function(){
            $("#poll_switch_2 > .active").removeClass('active')
            $("#poll_switch_2 > ."+ poll).addClass('active')
            active_poll_right_table=poll;
            if (poll!='MULTI'){
               
                var dic=getTypeDic(poll,'ada')
                buildTable(dic)
            }
            else {
                console.log('i_s_2')
                console.log(poll)
                var dic=getTypeDic(poll,'')
                buildTable(dic)
            }
        }
    )  
};

function refresh_right_table(){
    poll=active_poll_right_table
    check_statut()
    if (poll!='MULTI'){
       
        var dic=getTypeDic(poll,'ada')
        buildTable(dic)
    }
    else {
        console.log('i_s_2')
        console.log(poll)
        var dic=getTypeDic(poll,'')
        buildTable(dic)
    }
}
//gestion du clic sur le tableau de gestion des couches:
// - suppression de l'ancienne carte affich?
// - call de la nouvelle avec sa bounding box
// - maj de la variable activeLayer2
// function associ?aux cases du tableau quand on le refresh
function td_clic() {
    $(".t2 > tbody > tr > td").click(function(){
        $(".t2 > tbody > tr >  .active").removeClass('active')
        $(this).addClass('active')
        var id_source=($(this)[0].id).split("_")[1]
        o=liste_sources[id_source]
        $('#other_layers > a').remove()
        $('#other_layers > p').remove()
        $.ajax({
            url: "getMoreSources/"+id_source+".json",
            success : function(msg){
                //console.log(msg)
                var k=Object.keys(msg)
                $('#other_layers').append('<p>Autres sources pour le '+format_date(parseInt(o.daterun))+' '+ lib_ech[o.ech+1] + '</p>')
                //on parse chaque source
                for (i=0;i<k.length;i++) {
                    //construction du menu de gauche (du map-block1)
                    var ind=k[i]
                    var ob=msg[ind]
                    //console.log(ind)
                    id_but='tr_'+ind.toString()
                    if (!(ob.type==o.type)){
                        if (!(ob.type == 'fine')){
                            var html_btn='<a href="#" class="list-group-item point-item other_layers"  id="'+id_but+'"> <h4 class="list-group-item-heading" >'+ob.type+'</h4>J ' + ob.ech.toString() + '    <span class="glyphicon glyphicon-chevron-right hide"></span><span class="badge">Ready</span></a>'
                            //console.log(ob)             
                            $('#other_layers').append(html_btn)
                            if (ob.statut!=true){
                                $("#"+id_but + "  > .badge").css("background-color","red")
                            }
                        }
                    }
                }
                other_layers_clic()
            }   
        })
        if (o.statut == false){
            //alert('Pas de carte '+o.pol + ' disponible pour le '+ o.daterun + ', ??ce ?+ lib_ech[o.ech+1] + ', source : ' + o.type + " (code couleur rouge). Si d'autres sources sont disponible pour ce run / ??ce / polluant, elles s'afficheront en vers dans l'onglet \"autres sources\" qui apparait en cliquant sur uen case du tableau" )
        }
        else {
            if ( activeLayer2 != null) {
                map2.removeLayer(activeLayer2[1])
            }
            //workaround pour faire passer la variable id ds l'url

            url_bbox='{% url "bbox_raster" %}'
            
            
            img=img_raster_url(id_source)
            console.log(' ------- img -------- ')
            console.log(img)


            $.ajax({
                url: url_bbox,
                data : {
                    id:id_source
                },
                success : function(msg){
                    var anchors = [
                        [msg['ymax'], msg['xmin']], //haut gauche
                        [msg['ymax'], msg['xmax']], //haut droite
                        [msg['ymin'], msg['xmax']], //bas droite
                        [msg['ymin'], msg['xmin']]  //bas gauche
                    ];
                    var lay = L.imageTransform(img, anchors,{opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'}); 
         
                    lay.addTo(map2)
                    activeLayer2=[id_source,lay];
   
                    var tbl=meta_source_tbl(liste_sources[id_source])
                    $('#active_layer_div2 > table').remove()
                    $('#active_layer_div2').append(tbl)
                }
            })
        }
        //console.log(url_bounds)
    })
};

function other_layers_clic() {
    $(".other_layers").click(function(){
        var id_source=($(this)[0].id).split("_")[1]
        console.log(id_source)

        if ( activeLayer2 != null) {
            map2.removeLayer(activeLayer2[1])
        }
        //workaround pour faire passer la variable id ds l'url

        url_bbox='{% url "bbox_raster"  %}'
        img = img_raster_url(id_source)
        console.log(img)

        $.ajax({
            url: url_bbox,
                data : {
                    id:id_source
                },
            success : function(msg){
                var anchors = [
                    [msg['ymax'], msg['xmin']], //haut gauche
                    [msg['ymax'], msg['xmax']], //haut droite
                    [msg['ymin'], msg['xmax']], //bas droite
                    [msg['ymin'], msg['xmin']]  //bas gauche
                ];
                var lay = L.imageTransform(img, anchors,{opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});  
                lay.addTo(map2)
                activeLayer2=[id_source,lay];
                console.log(id_source.toString())
                var tbl=meta_source_tbl(liste_sources[id_source])
                $('#active_layer_div2 > table').remove()
                $('#active_layer_div2').append(tbl)
            },
            error : function(msg) {
                alert(msg)
            },  statusCode: {
    404: function() {
      alert( "page not found" );
    }
  }
        })
        

    })
        
}
/* --------- FIN DU MAP-BLOCK2 -------- */

function meta_source_tbl(obj){
    console.log(obj)
    console.log(obj.daterun)
    var tbl='<table class="table t_meta"><tbody><tr><th scope="row">Polluant : </th><td>'+obj.pol+'</td></tr><tr><th scope="row">Modèle : </th><td>'+obj.type+'</td></tr><tr><th scope="row">Date run </th><td>'+format_date(parseInt(obj.daterun))+'</td></tr><tr><th scope="row">Echeance </th><td>'+lib_ech[obj.ech+1]+'</td></tr></tbody></table>';
    
    return tbl
}
function switch_source() {
    if (activeLayer2==undefined){
        if (dumb >= 3){
            alert ('Pas de carte, pas de chocolat')
        }
        else {
            alert("Veuillez tout d'abord s?ctionner une carte valide dans la fen?e de droite")
            dumb+=1;
        }
    }
    else {
        sources=[]
        $('#switch_input > option').remove()
        for (i in prevs) {
            if (typeof i === undefined){
                console.log("i => undefined")
            }
            else {
                pol=prevs[i][0]
                ech=prevs[i][1]
                if ( pol != "MULTI"){
                    var lib=pol+ ' ' + ech.toString()
                    var val=i
                     $('#switch_input').append('<option value='+val +'>'+lib+'</option>')
                }
            }
        }

        // for (i=0 ;i<old_sources.length; i++) {
            // val=old_sources[i]
            // $('#switch_input').append('<option value='+val +'>'+val+'</option>')
        // }
        id_new_source=activeLayer2[0];
        ob=liste_sources[id_new_source]
        str_source=ob.pol + " / " + ob.daterun + " / "+ lib_ech[ob.ech+1] + " / " + ob.type
        $("#new_source > option").remove()
        $('#switch_source_div').show()
        $("#new_source").append("<option value="+id_new_source+" selected disabled hidden>"+str_source+"</option>")
    }
}
function remove_switch_form() {
    $('#switch_source_div').hide()
}
function validate_switch_btn(){
    id_prev=$("#switch_input > option:selected").val()
    id=$("#new_source > option:selected").val()
    console.log('id_prev : ' + id_prev)
    console.log('id : '+ id)
    update_source(id_prev,id)
    id_but=$(".active")[1].id
    switch_map_1(id_but)
    console.log(id_but)
}
function remove_multi_form() {
    $("#multi_div").hide()
    $("#mask").hide()
}
function calculate_multi_all(){
    var url='{% url "img_multi" %}'

    for (i=0;i<4;i++)
    $.ajax({
        url: url,
        async : false,
        data : {
            ech : i             
        }
        ,success : function(){
            console.log('success multi => a check')
            console.log(msg)
        }
        ,error  : function (msg) {
            console.log(msg)
        }
    })
}
function calculate_multi(){
    $("#mask").hide()
    $("#multi_div").hide()
    show_msg()
    $("tr > .td_valid > input:checked").each(function(i){
        i=parseInt($(this).attr('id').slice(-2))+1
        msg_add_content('<div class="row msg-div">Calcul du j'+i.toString()+' => en cours ...</div>')
        var url='{% url "img_multi" %}'

        console.log(i)
        $.ajax({
            url: url,
            async : false,
            data : {
                ech : i             
            }
            ,success : function(){
                console.log('success multi => a check')
                refresh_right_table()
                msg_add_content('<div class="row msg-div">Calcul du j'+i.toString()+' => OK </div>')
            }
            ,error  : function () {
                msg_add_content('<div class="row msg-div">Calcul du j'+i.toString()+' => Echec </div>')
            }
        })
    })

    // var url="/raster/img/raster_multi_0.png";

}
function multi_form_show(){
    // Afficher le formulaire d'insertion
    //rappel : prevs format => {id_prev::int : [poll::string,ech::int[0-3]]}
    console.log("vmf")
    $("#mask").show()
    $("#multi_div").show()
    tbl=$("#multi_tbl")
    tbody=$("#multi_tbl > tbody")
    for (i in prevs) {
        if (typeof i === undefined){
            console.log("i => undefined")
        }
        else {
            pol=prevs[i][0]
            if (pol.toLowerCase()!='multi'){
                
                ech=prevs[i][1]
                console.log(ech)
                overlayButId="lay_btn_"+i.toString()
                console.log(overlayButId)
                id_source=overlayLayers1[overlayButId]
                console.log(id_source)
                src=liste_sources[id_source ]
                lib=lib_ech[ech+1].toString()
                console.log(lib)
                id_row='tr_'+ech.toString()+"_"+pol.toLowerCase()
                console.log(id_row)
                $("#"+id_row+" > .td_poll_source").text(src['pol'])
                $("#"+id_row+" > .td_type").text(src['type'])
                $("#"+id_row+" > .td_date").text(src['daterun'])
                $("#"+id_row+" > .td_ech_source").text(src['ech'])
                
            }
        }
    }
}

     


/* Chargement du fond de carte */
// comme toutes les couches, on est oblig?e l'instancier une fois par objet map...
var mapbox_light = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoicmh1bSIsImEiOiJjaWx5ZmFnM2wwMGdidmZtNjBnYzVuM2dtIn0.MMLcyhsS00VFpKdopb190Q', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery ?<a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.light',
    opacity: 1.,
});   
mapbox_light.addTo(map);
var mapbox_light2 = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoicmh1bSIsImEiOiJjaWx5ZmFnM2wwMGdidmZtNjBnYzVuM2dtIn0.MMLcyhsS00VFpKdopb190Q', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery ?<a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.light',
    opacity: 1.,
});   
mapbox_light2.addTo(map2);



//fonction popup sur champ 'nom'
//utilis?ar les couches vecteurs
function onEachFeature(feature, layer) {
        var popupContent="";
        if (feature.properties && feature.properties.nom) {
            popupContent += feature.properties.nom;
        }

        layer.bindPopup(popupContent);
    }
function onEachFeatureDisp(feature, layer) {
        var popupContent="";
        if (feature.properties && feature.properties.lib_court_) {
            popupContent += feature.properties.lib_court_;
        }

        layer.bindPopup(popupContent);
    }
// Enregistrement du polluant et de l'??ce par defaut



var reg_aura;
$.ajax({
    url: '{% url "reg_aura"  %}',
    success : function(msg){
        //j=JSON.parse(msg)
        reg_aura = L.geoJSON(
            msg,
            {
                onEachFeature: onEachFeature,
                style : myStyle
            }
        )
        vectorLayers['reg_aura']= {'objet' : reg_aura}
        //clone grace au plugin clonelayer pour permettre d'afficher sur les 2 frames
        var  reg_aura_2 = cloneLayer(reg_aura);
        vectorLayers['reg_aura_2']= {'objet' : reg_aura_2}

    }
});
var disp_reg;
var disp_reg_2;

$.ajax({
    dataType: "json",
    url: "{% static 'raster/vector_files/disp_reg_aura_3857.geojson' %}",
    success : function(msg){
        //j=JSON.parse(msg)
        disp_reg= L.geoJSON(
            msg,
            {
                onEachFeature: onEachFeatureDisp,
                style : myStyle
            }
        )
        vectorLayers['disp_reg']= {'objet' : disp_reg}
        //clone grace au plugin clonelayer pour permettre d'afficher sur les 2 frames
        var  disp_reg_2 = cloneLayer(disp_reg);
        vectorLayers['disp_reg_2']= {'objet' : disp_reg_2}

    }
});


var layer_sites_fixes;
$.ajax({
    url: '{% url "sites_fixes"  %}',
    success : function(msg){
        
        layer_sites_fixes = L.geoJSON(
            msg,
            {
                onEachFeature: onEachFeature,
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, sites_fixes_style);
                }
            }
        )
        
        vectorLayers['layer_sites_fixes']= {'objet' : layer_sites_fixes}
        //clone grace au plugin clonelayer pour permettre d'afficher sur les 2 frames
        var  layer_sites_fixes_2 = cloneLayer(layer_sites_fixes);
        vectorLayers['layer_sites_fixes_2']= {'objet' : layer_sites_fixes_2}

    }
});
$(function() {
    $('.vector-layer').children().click( function() {
        var id = $(this).attr('id')

        substr = "close";
        string= $('#'+id + ' > span').attr('class')
        if (string.indexOf(substr) > -1) {
            $('#'+id + ' > span').removeClass('glyphicon-eye-close')
            $('#'+id + ' > span').addClass('glyphicon-eye-open')
        }
        else {
            $('#'+id + ' > span').removeClass('glyphicon-eye-open')
            $('#'+id + ' > span').addClass('glyphicon-eye-close')
        }
        if ($(this).closest("#map-block1").length == 1){
            ob=vectorLayers[id]['objet']
            if (map.hasLayer(ob)){
                console.log(ob)
                ob.removeFrom(map)
            }
            else {
                
                ob.addTo(map)
            }
        }
        if ($(this).closest("#map-block2").length == 1){
            ob=vectorLayers[id]['objet']
            console.log(ob)
            if (map2.hasLayer(ob)){             
                ob.removeFrom(map2)
            }
            else {
                ob.addTo(map2)
            }
        }
    })
})
/*cacher les onglets fine ?elle au clic sur la croix*/
/*
$(function(){
    $('.hide-fine-btn').click(function (){
        $(this).parent().addClass('hide');
    })
})
$(function(){
    $('.show-fine-btn').click(function (){
        // Ajout de la couche choisie
        overlayLayers[$(this).parent()[0].id]["objet"].addTo(map);
    })
    
})
*/


/* Fonctions ?cut? on click */
map.on('click', function(e) {   
    val=''
    coords = e.latlng;
    console.log(coords)
    if (activeLayer1===undefined){
        console.log("pas de carte affich?.. pas de carte... pas de concentration")
    }
    else {
        id_source=activeLayer1[0]
        url='{% url 'get_pixel'  %}'
        
        console.log(url)
        $.ajax({

            url:url,
            data : {
                id : id_source,
                x : Math.round(coords['lng']*1000000),
                y : Math.round(coords['lat']*1000000)
                
            },
            success : function(msg){
                // j=JSON.parse(msg)
                // console.log(msg)
                // console.log(msg['val'])
                // var popup = L.popup()
                // .setLatLng(coords)
                // .setContent('valeur brute corrig?: ' + msg['val'][0].toString()+ ' <br/>  sous indice : ' + msg['val'][1].toString())
                // .openOn(map);

                // var k=Object.keys(msg)
                $('#t1-v1').text(msg['val'][0].toString())
                $('#t1-v2').text(msg['val'][1].toString())

            }
        });
    }

});  
/* map.on('mousemove', function(e) {   
    val=''
    coords = e.latlng;
    if (activeLayer1===undefined){
        console.log("pas de carte affich?.. pas de carte... pas de concentration")
    }
    else {
        id_source=activeLayer1[0]
        $.ajax({

            url: '{% url 'indice_request'  %}',
            data : {

                x : coords['lng'],
                y : coords['lat']
                
            },
            success : function(msg){
                // j=JSON.parse(msg)
                console.log(msg)
                // console.log(msg['val'])
                // var popup = L.popup()
                // .setLatLng(coords)
                // .setContent('valeur brute corrig?: ' + msg['val'][0].toString()+ ' <br/>  sous indice : ' + msg['val'][1].toString())
                // .openOn(map);

                // var k=Object.keys(msg)
                // $('#t1-v1').text(msg)

            }
        });
    }

});  */  
map2.on('click', function(e) {   
    val=''
    coords = e.latlng;
    console.log(coords)
    if (activeLayer2===undefined){
        console.log("pas de carte affich?.. pas de carte... pas de concentration")
    }
    else {
        id_source=activeLayer2[0]
        url='{% url 'get_pixel'  %}'
       
        console.log(url)
        $.ajax({

            url:url,
            data : {
                id : id_source,
                x : Math.round(coords['lng']*1000000),
                y : Math.round(coords['lat']*1000000)
                
            },
            success : function(msg){
                //j=JSON.parse(msg)
                $('#t2-v1').text(msg['val'][0].toString())
                $('#t2-v2').text(msg['val'][1].toString())
            }
        });
    }
}); 
/* Leaflet.draw */
drawnItems = L.featureGroup().addTo(map);

map.addControl(new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
        poly: {
            allowIntersection: false
        }
    },
    draw: {     
        polygon: {
            allowIntersection: false,
            showArea: true
        },
        marker : false,
        circle: false,
        polyline: false,
        rectangle: false,
    },
    position: 'topleft'
}));

// Action apr?dessin
map.on(L.Draw.Event.CREATED, function (event) {
    var layer = event.layer;
    var type = event.layerType;

    if (type === 'marker') {
        corr_coords = [];
        corr_coords.push(layer._latlng.lng, layer._latlng.lat);
    };      

    if (type === 'polygon') {
    
        corr_coords = [];
        for (var point in layer._latlngs[0]) {
            corr_coords.push([layer._latlngs[0][point].lng, layer._latlngs[0][point].lat]);
        };          
    };          
    
    /* Afficher le formulaire d'insertion */
    $('#modal_corr_form').modal('show');    
    ($('#ModalCorrTitle'))[0].innerText = "Correction de la carte " + corr_pollutant;
    ($('#corr_form_val'))[0].value = "";

    
    /* Ajout de l'?ment cr?au groupe */
    drawnItems.addLayer(layer);
    drawLayer=layer
});

// Action apr?modification de forme
map.on('draw:edited', function (event) {
    var layers = event.layers;
    layers.eachLayer(function (layer) {
    
        // Afficher le formulaire d'insertion
        $('#modal_corr_form').modal('show');
        
    });
});

/* Fonction ?cut?lors de l'envoi du formulaire de correction */ 
$("#submitFormCorr").click(function (e) {
    console.log("envoi");
    
    e.preventDefault();

    var corr_value = ($('#corr_form_val'))[0].value;
    var corr_min = ($('#corr_form_min'))[0].value;
    var corr_max = ($('#corr_form_max'))[0].value;
    // var corr_ssup = ($('#corr_form_ssup'))[0].value;
	var corr_ssup=""
    var id_source=activeLayer1[0]
    console.log("V?fication du formulaire");

    /* V?fication du formulaire */   
    if (corr_coords == "" || corr_coords == 'undefined' || corr_coords == []) {
        console.log("Erreur verif formulaire: coords");
        $("#error_tube").show(); // FIXME: Pas cr?
        return;
    };
    if (corr_value == "" || corr_value == 'undefined') {
        console.log("Erreur verif formulaire: valeur");
        $("#error_tube").show(); // FIXME: Pas cr?
        return;
    };
    if (corr_min == "" || corr_min == 'undefined' || corr_min == []) {
        console.log("Erreur verif formulaire: min : set min = 0");
        corr_min=0
        //$("#error_tube").show(); // FIXME: Pas cr?

    };
    if (corr_max == "" || corr_max == 'undefined' || corr_max == []) {
        console.log("Erreur verif formulaire: max : set max = 9999");
        corr_max=9999
        //$("#error_tube").show(); // FIXME: Pas cr?

    };
    if (corr_ssup == "" || corr_ssup == 'undefined' || corr_ssup == []) {
        console.log("Erreur verif formulaire: seuil sup : set ssup = 9999");
        corr_ssup=9999
        $("#error_tube").show(); // FIXME: Pas cr?

    };
    console.log("***********************");
    console.log("Submission du formulaire de correction:");
    console.log("Source: " + id_source);
    console.log("Coords: " + corr_coords); 
    console.log("Valeur: " + corr_value);
    console.log("Minimum: " + corr_min);
    console.log("Maximum: " + corr_max);
    console.log("Seuil sup: " + corr_ssup);
    console.log("***********************");
    // var csrftoken = getCookie('csrftoken');
    // console.log(csrftoken);
    // $.ajaxSetup({   headers: {  "X-CSRFToken": csrftoken  }  });

    console.log(corr_coords)
    var wkt = $.geo.WKT.stringify( {
        type: 'Polygon',
        coordinates: [corr_coords,[]]
    } );
    console.log(wkt)
    // Execution de la transaction Ajax - Page JV
    $.ajax({
        type: "POST",

        //headers: { "X-CSRFToken": csrftoken },
        url: "{% url 'alter_raster' %}",
        data: {
            source:id_source,
            value: corr_value,
            minimum : corr_min,
            maximum : corr_max,
            ssup : corr_ssup,
            coords: JSON.stringify(corr_coords)           

        },
        dataType: 'json',

        success: function(response,textStatus,jqXHR){
            
            console.log("SUCCES!");
            console.log(response);
            
            // Fermeture du formulaire 
            $("#modal_corr_form").modal('hide');
               
            //null si on a pas encore initialis?inutile si on affiche un polluant par defaut)
            if ( activeLayer1 != null) {
                map.removeLayer(activeLayer1[1])
            }
            id_source = overlayLayers1[id_but]
            

            url_bbox='{% url "bbox_raster" %}'
            img=img_raster_url(id_source)

            $.ajax({
                //recup de scoins de la carte necessaires pour que leaflet affiche le png
                url: url_bbox,
                data : {
                    id:id_source
                },
                success : function(msg){
                    anchors = [
                        [msg['ymax'], msg['xmin']], //haut gauche
                        [msg['ymax'], msg['xmax']], //haut droite
                        [msg['ymin'], msg['xmax']], //bas droite
                        [msg['ymin'], msg['xmin']]  //bas gauche
                    ];
                    console.log(anchors)
                    lay = L.imageTransform(img, anchors, {opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});     
                    lay.addTo(map)
                    activeLayer1=[id_source,lay];
                    
                    console.log(id_source.toString())
                    var tbl=meta_source_tbl(liste_sources[id_source])
                    $('#active_layer_div1 > table').remove()
                    $('#active_layer_div1').append(tbl)
                }
            })      
        },
        error: function (request, error) {
            console.log(request);
            
            console.log("ERROR");
            console.log(arguments);
            console.log("Ajax error: " + error);
            $("#error_tube").show();
        },        
    });
    drawLayer.removeFrom(map)
 
}); 

/* Fonction ?cut?lors de l'annulation de l'envoi du formulaire de correction */
$("#reset").click(function (e) {
    console.log("Annulation de l'envoie, on conserve l'objet pour ?ntuelles modifications.")
});
function post_test(){
    $.ajax({
        type: "POST",
        url : "{% url 'trajet_request' %}",
        data : { type:"FeatureCollection",features:[{type:"Feature",geometry:{type:"MultiLineString",coordinates:[[[5,45.685905],[5.000280,45.6859]],[[5.000280,45.6859],[5.000280,45.6840]]]}}]},
        dataType : 'json',       
        success : 
            function(msg) {
                console.log(msg)
            }
    })
}    
/* 
$( ".toggle-right-mode" ).mouseenter(function() {
    $(".right-btn").show()
    $("#right-btn-chevron").hide()
})
$( ".toggle-right-mode" ).mouseleave(function() {
    $(".right-btn").hide()
    $("#right-btn-chevron").show()
})
$('#stat-block').hide()
function show_map2_clic(){
    $('#stat-block').hide()
    $('#map-block2').show()

}
function show_stats_clic(){
    $('#map-block2').hide()
    $('#stat-block').show()
} */
// using jQuery
// function getCookie(name) {
    // var cookieValue = null;
    // if (document.cookie && document.cookie != '') {
        // var cookies = document.cookie.split(';');
        // for (var i = 0; i < cookies.length; i++) {
            // var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            // if (cookie.substring(0, name.length + 1) == (name + '=')) {
                // cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                // break;
            // }
        // }
    // }
    // return cookieValue;
// }

function test(){
    console.log('iug')
    $.ajax({
        type: "POST",
        //csrfmiddlewaretoken: '{{ csrf_token }}',
        // headers: { "X-CSRFToken": getCookie("csrftoken") },
        url: "{% url 'test_ajax' %}",
        data: {
            source:1000    
          /*  type: 'point',
            delta: 5,
            lon: 6,
            lat: 45*/  
        },
        dataType: 'json',
        // beforeSend:function( jqXHR, settings){
            // jqXHR.latlng = tmp_latlng;
            // jqXHR.icones = icones;
            // jqXHR.image = e.target.result;
            // jqXHR.tubes_layer = tubes_layer;
        // },
        success: function(response,textStatus,jqXHR){    
            console.log("SUCCES!");
            console.log(response);

        },
        error: function (request, error) {
            console.log(request);
            
            console.log("ERROR");
            console.log(arguments);
            console.log("Ajax error: " + error);
            $("#error_tube").show();
        },        
    }); 
}
function launch_async(func){
    show_msg()
    func()
}
function get_stats_reg(){
    // show_msg()
    url_img='{% url "calcul_stats_reg"  %}'
    log_dashboard('statistiques_reglementaires','get_stats_reg',1,'INFO',"début du calcul des stats")
    c=0
    for (i in overlayLayers1){
        
        id_prev=i.split('_')[2]     
        id=overlayLayers1[i]
        
        // msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : en cours ... </div>')
        $.ajax({
            url : url_img,
            async : false,
            data : { 
                id_prev : id_prev
            },
            success: 
                function(msg){

                },
            error:      
                function(msg){

                },

        })
    }

    log_dashboard('statistiques_reglementaires','get_stats_reg',100,'INFO',"fin du calcul des stats")

    
}
function launch_stats(){
	get_stats_reg_unique(id_prev)
}
function get_stats_reg_unique(id_prev){
    show_msg()
    url_img='{% url "calcul_stats_reg"  %}'
    msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : en cours ... </div>')
    $.ajax({
        url : url_img,
        async : false,
        data : { 
            id_prev : id_prev
        },
        success: 
            function(msg){
                prevs[id_prev]['stats']=msg
                msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : OK </div>')
            }
        ,error : function () {
            msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : échec </div>')
        }
    })
}

function launch_BQA_unique(){
    $.ajax({
        url : '{% url "launch_BQA_unique"  %}',
        async : false,
        data : { 
            id_prev : id_prev
        },
        success: 
            function(msg){
                prevs[id_prev]['ibg']=msg
                msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : OK </div>')
            }
        ,error : function () {
            msg_add_content('<div> ' +prevs[id_prev][0].toString() +' - '+ prevs[id_prev][1].toString() + ' : échec </div>')
        }
    })
}
function launch_BQA(){
    log_dashboard('calcul_bassin_grenoblois','launch_BQA',1,'INFO',"calcul de l'indice du bassin grenoblois en cours")
    $.ajax({
        url : '{% url "launch_BQA" %}',
        async : false,
        success: function(msg){
            log_dashboard('calcul_bassin_grenoblois','launch_BQA',100,'INFO','insertion base transalpair terminée pour les 4 échéances')
        },
        error : function(){
            log_dashboard('calcul_bassin_grenoblois','launch_BQA',100,'ERROR',"erreur lors du calcul ou de l'insertion transalpair")
        }
    })
}
function get_indice_com(){
    c=0
    log_dashboard('indices_communaux','get_indice_com',1,'INFO','calcul des indices communaux')
    url_img='{% url "calcul_indice_com"  %}'
    for (i in overlayLayers1){
        id_prev=i.split('_')[2]
        id=overlayLayers1[i]
        if (liste_sources[id].pol=='MULTI'){

            console.log(id_prev)
            $.ajax({
                url : url_img,
                async : false,
                data : { 
                    id_prev : id_prev
                },
                success: 
                    function(msg){
                       c+=20 
                        prevs[id_prev]['indice_com']=msg
                        log_dashboard('indices_communaux','get_indice_com',c,'INFO','calcul des indices communaux pour id_prev= '+ id_prev.toString())
                        
                    },
                error : function (){
                    c+=10
                    log_dashboard('indices_communaux','get_indice_com',c,'WARNING','calcul des indices communaux pour id_prev= '+ id_prev.toString())

                    
                }
            })
        }
    }
    if (c<80){
         log_dashboard('indices_communaux','get_indice_com',100,'ERROR','erreur sur les indices communaux')
    }
    else {
         log_dashboard('indices_communaux','get_indice_com',100,'INFO','fin du calcul des indices communaux')
    }
}

function launch_commentaire(ech){
    $("#commentaire-div").show()
    $("#echeance-input").val(ech)
    d=format_date_ymd(today)
    $.ajax({
        url : '{% url "get_commentaire" %}',
        async : true,
        data : { 
            date : d
        },
        success: 
            function(comm){
                c=(comm['comment'])
                
                $('#commentaire-text-input').val(c)
            }
    })
    $("#mask").show()
}
function remove_commentaire_form() {
    $("#commentaire-div").hide()
    $("#mask").hide()
}
function valid_commentaire(){
    // var csrftoken = getCookie('csrftoken');
    ech=$('#echeance-input').val()
    console.log(ech)
    comm=$('#commentaire-text-input').val()
    console.log(comm)
    $("#commentaire-div").hide()
    $("#mask").hide()
    $.ajax({   
        type: "POST",
        // headers: { "X-CSRFToken": csrftoken },    
        url: '{% url "save_commentaire"   %}',
        data: {
            date_prev:today,
            commentaire:comm
        },
        //dataType: 'json',
        success: function(msg){

            console.log(msg)
        }

    })
}
function export_low() {
    log_dashboard('basse_def_image','export_low',1,'INFO',"début de l'export des images basse def")
    c=0
    for (i in overlayLayers1){

        id_source= overlayLayers1[i]
        id_prev=i.split('_')[2]
        console.log(id_source)
        $.ajax ({
         async : false,
          url: '{% url "export_low" %}',
          data : {
            id_source:id_source,
            id_prev:id_prev
          },
          success : function(){

          },
          error : function () {

          }
        })      
    }

        log_dashboard('basse_def_image','export_low',100,'INFO',"succès de l'export des images basse def")

}
function export_low_val() {
    log_dashboard('basse_def_val','export_low_val',1,'INFO',"début de l'export des ss_indices basse def")
    c=0
    for (i in overlayLayers1){

        id_source= overlayLayers1[i]
        id_prev=i.split('_')[2]
        console.log(id_source)
        $.ajax ({
         async : false,
          url: '{% url "export_low_val" %}',
          data : {
            id_source:id_source,
            id_prev:id_prev
          },
        success : function(){
 
          },
        error : function () {
          

          }
        })      

    }

        log_dashboard('basse_def_val','export_low_val',100,'INFO',"succès de l'export des ss_indices basse def")

}
function merge_mi_fine(id_prev,id_source) {
    if ( activeLayer1 != null) {
        map.removeLayer(activeLayer1[1])
        console.log(activeLayer1[1])
    }
    id_source = overlayLayers1[id_but]
    
    console.log('id_source : ' + id_source.toString())
    //workaround pour faire passer la variable id ds l'url

    url_bbox='{% url "bbox_raster" %}'

    img=mi_fine_url(id_source,id_prev)



    // s1="'{% "
    // s2=" %}'"
    // s3=s1 + s + s2
    // console.log(s1 + s + s2)
    $.ajax({
        //recup de scoins de la carte necessaires pour que leaflet affiche le png
        url: url_bbox,
        data : {
            id:id_source
        },
        success : function(msg){
            anchors = [
                [msg['ymax'], msg['xmin']], //haut gauche
                [msg['ymax'], msg['xmax']], //haut droite
                [msg['ymin'], msg['xmax']], //bas droite
                [msg['ymin'], msg['xmin']]  //bas gauche
            ];
            //console.log(anchors)
            lay = L.imageTransform(img, anchors, {opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});     
            lay.addTo(map)
            activeLayer1=[id_source,lay];
            
            //console.log(id_source.toString())
            var tbl=meta_source_tbl(liste_sources[id_source])
            $('#active_layer_div1 > table').remove()
            $('#active_layer_div1').append(tbl)
        },
        error : function(msg) {
            alert(msg)
        },
          statusCode: {
            404: function() {
                alert( "page not found" );
            }
        }
    }) 
}
function export_hd() {
    n=0
 
    for (i in overlayLayers1){

        if (n<1){
            id_source= overlayLayers1[i]
            
            id_prev=i.split('_')[2]
            console.log(id_source)
            $.ajax ({
              async : true,
              url: '{% url "merge_fine" %}',
              data : {
                id_source:id_source,
                id_prev:id_prev
              },
            success : function(){
                  $.ajax ({
                      async : true,
                      url: '{% url "callback_merge" %}',
                      data : {
                        id_source:id_source,
                        id_prev:id_prev
                      }
                    })
            },
            error : function () {

            }

        })
        n+=1

        }
       
        else  {
            id_source= overlayLayers1[i]
            
            id_prev=i.split('_')[2]    
            console.log(id_source)
            $.ajax ({
              async : false,
              url: '{% url "merge_fine" %}',
              data : {
                id_source:id_source,
                id_prev:id_prev
              },
                success : function(){
                  $.ajax ({
                      async : true,
                      url: '{% url "callback_merge" %}',
                      data : {
                        id_source:id_source,
                        id_prev:id_prev
                      }
                    })
                },
                error : function () {

                }
            })
       
        n=0
        }

    }
}
function mi_fine_url(id_source,id_prev){
    var img='';
    url_img='{% url "mi_fine_url" %}'
    $.ajax({
        url:url_img,
        async : false,
        data : { 
            id_source : id_source,
            id_prev : id_prev
        },
       
        success : function(msg){
            img=msg
        }
    })
    return img;
}
function img_raster_url(id_source){
    var img='';
    url_img='{% url "img_raster_url" %}'
    $.ajax({
        url:url_img,
        async : false,
        data : { 
            id_source : id_source
        },
       
        success : function(msg){
            img=msg
        }
    })
    return img;
}
function fake()    {
      $.ajax({
        url:'{% url "fake" %}',
        async : false,

        success : function(msg){
            console.log(msg)
        }
    })
}  

function show_mask(){
    $('#mask').show()
}
function hide_mask(){
    $('#mask').css('display','none')
}
function show_msg(){

    $('.msg').css('display','block')
    $('.msg').append('<div class="container-fluid" id="msg-content"></div>')
    show_mask()
}
function msg_add_content(html){
    $('.msg > #msg-content').append(html)
}
function close_msg(){
    hide_mask()
    $('.msg > #msg-content').remove()
    $('.msg').css('display','none')
}
function preprocess_files(){
    $.get({
        url:"http://inf-tools/dashboard/log",
        data : {
            id : 'preprocess_files',
            script : 'carinev3/raster',
            etape : 1 ,
            type : 'INFO',
            m : 'début régénération des sources'
        }
    })
    $.ajax({
        url:'{% url "preprocess_files" %}',
        async : true,
        success : function(msg){
            check_statut()
            $("#poll_switch_1 > ."+active_poll_left_table ).click()
            refresh_right_table()
            process_files=true
            $.get({
                url:"http://inf-tools/dashboard/log",
                data : {
                    id : 'preprocess_files',
                    script :'carinev3/raster',
                    etape : 100,
                    type : 'INFO',
                    m : 'régénération des sources terminée'
                }
            })
        },
        error : function(msg){
            $.get({
                url:"http://inf-tools/dashboard/log",
                data : {
                id : 'preprocess_files',
                script : 'carinev3/raster',
                etape : 100,
                type : 'ERROR',
                m : 'régénération des sources incomplète, fichiers probablement corrompus'
                }
            })
        }
    })
    
}
function statsShow(id_prev){
    obs=prevs[id_prev]['stats']
    $('#mask').show()
    $('#stats_tbl >  tbody').remove()
    $('#stats_div').show()
    $('#stats_tbl').append('<tbody></tbody>')
    for (i in obs){
        console.log(i)
        ligne = getStatHTML(i,obs[i])
        console.log(ligne)
        $('#stats_tbl >  tbody').append(ligne)
    }
}
function bool_lib(b){
    dep_lib=''
    if (b==false){
        dep_lib='non'
    }
    else if (b==true){
        dep_lib='oui'
    }
    return dep_lib
}
function getStatHTML(id,obj){
    lib=obj['lib']
    dpa=obj['depassement_pop_alerte']
    dpa=bool_lib(dpa)
    dpi=obj['depassement_pop_info']
    dpi=bool_lib(dpi)
    dsa=obj['depassement_surf_alerte']
    dsa=bool_lib(dsa)
    dsi=obj['depassement_surf_info']
    dsi=bool_lib(dsi)
    pea=obj['pop_exp_alerte']
    pei=obj['pop_exp_info']
    pepa=obj['pop_exp_perc_alerte']
    pepi=obj['pop_exp_perc_info']
    sea=obj['surf_exp_alerte']
    sei=obj['surf_exp_info']
    sepa=obj['surf_exp_perc_alerte']
    sepi=obj['surf_exp_perc_info']
    tr_dep_cls='tr_grey'
    if (dsi=='oui'){
        tr_dep_cls='tr_orange'      
    }
    if (dpi=='oui'){
        tr_dep_cls='tr_orange'
    }
    if (dsa=='oui'){
        tr_dep_cls='tr_red'     
    }
    if (dpa=='oui'){
        tr_dep_cls='tr_red'
    }
    s='<tr class="'+tr_dep_cls+'">'+
        '<td>'+id+'</td>'+
        '<td>'+lib+'</td>'+
        '<td>'+sei+'</td>'+
        '<td>'+sepi+'</td>'+
        '<td>'+dsi+'</td>'+
        '<td>'+pei+'</td>'+
        '<td>'+pepi+'</td>'+
        '<td>'+dpi+'</td>'+
        '<td>'+sea+'</td>'+
        '<td>'+sepa+'</td>'+
        '<td>'+dsa+'</td>'+
        '<td>'+pea+'</td>'+
        '<td>'+pepa+'</td>'+
        '<td>'+dpa+'</td>'+
    '</tr>'
    return s
}
function remove_stats_form(){
    $('#mask').hide()
    $('#stats_div').hide()
}
function contactSMILE(){
    log_dashboard('contact_smile','contactSMILE',1,'INFO',"tentative de contact SMILE")
    $.ajax({
        url : 'ws_smile',
        success : function(msg){
            if (JSON.parse(msg)["result"]==1){
                log_dashboard('contact_smile','contactSMILE',100,'INFO',"succès de la tentative de contact SMILE")
                alert( " import SMILE activé, les résultats seront disponibles d'ici une vingtaine de minutes sur le site" )
            }
            else {
                alert( " problème avec l'import SMILE, essayer de cliquer sur 'REDIFFUSER' (outils > REDIFFUSER). Si le problème persiste, contacter le service informatique. " )
                log_dashboard('contact_smile','contactSMILE',100,'ECHEC',"échec de la tentative de contact SMILE")
            }
        }
    })
}
function validPrevi(){
    log_dashboard('validation_generale','validPrevi',1,'INFO',"clic validation, début des calculs")
	hideConfirmValidPrevi()
    calculate_multi_all()
    launch_BQA()
    get_stats_reg()
    get_indice_com()
    export_low_val()
    export_low()
    export_hd()
    contactSMILE()
    log_dashboard('validation_generale','validPrevi',100,'INFO',"fin des calculs")
    export_scp()
    }
function confirmValidPrevi(){
	$('#mask').show()
	$('#confirm-valid-div').show()
}
function hideConfirmValidPrevi(){
	$('#mask').hide()
	$('#confirm-valid-div').hide()
}
function get_expertises(id_source){
    $.ajax({
        url:'{% url "get_expertises" %}',
        async : false,
        data : { 
            id_source : id_source
        },
       
        success : function(msg){
            exps=msg
        }
    })
    return exps;
}
function set_expertises(id_exp,bool){
    $.ajax({
        url:'{% url "set_expertises" %}',
        async : false,
        data : { 
            id_exp : id_exp,
			active : bool
        },
       
        success : function(msg){
            exps=msg
        }
    })
    return exps;
}
function expMenu(id_source){
	exps=get_expertises(id_source)
	$(".table-corr").remove()
	console.log(id_but)
	
	html='<table class="table-responsive table-bordered table-corr"><tr><th>val</th><th data-toggle="tooltip" title="seuil minimum pour appliquer la correction">min</th><th data-toggle="tooltip" title="seuil maximum pour appliquer la correction">max</th><th>active</th></tr>'
	
	for (e in exps){
		console.log(e)
		ob=exps[e]
		id_cbx='cbx_'+ ob['id'].toString()
		var check='';
		if (ob['active']==true){
			check=' checked="checked "'
		}

		html+='<tr><td>'+ob.delta.toString()+'</td><td>'+ob.min.toString()+'</td><td>'+ob.max.toString()+'</td><td><input class="exp_cbx" id="'+id_cbx+'" type="checkbox" '+check+'></td></tr>'	

	}
	html+='</table>'
	$('#exp-btn').after(html)
	$( ".exp_cbx" ).change(function() {
		id=$(this)[0].id.split("_")[1]
        console.log(id)
		bool=$(this).is( ":checked" )
		set_expertises(id,bool)
        
		id_but=$(".active")[1].id
		switch_map_1(id_but)		
	})
}
$('.map-block').css('display','inline-block')
function switch_ecran() {
	var dis=$('.map-block').css('display')
	if (dis=='inline-block'){
		$('.map-block').css('display','inline')
		$('#map-block2').css('display','none')
	}
	else {
		$('.map-block').css('display','inline-block')
		$('#map-block2').css('display','inline-block')
	}
}
function drag_start(event) {
    var style = window.getComputedStyle(event.target, null);
    event.dataTransfer.setData("text/plain",
    (parseInt(style.getPropertyValue("left"),10) - event.clientX) + ',' + (parseInt(style.getPropertyValue("top"),10) - event.clientY));
} 
function drag_over(event) { 
    event.preventDefault(); 
    return false; 
} 
function drop(event) { 
    var offset = event.dataTransfer.getData("text/plain").split(',');
    var z = document.getElementById('drag_stats_btn');
    z.style.left = (event.clientX + parseInt(offset[0],10)) + 'px';
    z.style.top = (event.clientY + parseInt(offset[1],10)) + 'px';
    event.preventDefault();
    return false;
} 
var dm = document.getElementById('drag_stats_btn'); 
dm.addEventListener('dragstart',drag_start,false); 
document.body.addEventListener('dragover',drag_over,false); 
document.body.addEventListener('drop',drop,false);
function log_dashboard(id_process,script_name,step,lvl,msg){
        $.get({
        async : true,
        url:"http://inf-tools/dashboard/log",
        data : {
            id : id_process,
            script : script_name,
            etape : step,
            type : lvl,
            m : msg
        }
    })
}
function export_scp(){
    $.ajax ({
        async : true,
        url: '{% url "export_scp" %}',
        data: {
            type : ['hd_val','hd_img','bd_val','bd_img']
        },
        succes : function (msg){
            alert(msg)
        }
        
    })
}