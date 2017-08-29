/* Variables globales pour stocker les paramètres de correction */
var corr_pollutant = "";
var corr_echeance = "";
var corr_type = "";
var corr_coords = [];
var corr_value = "";

var lib_ech=["j-1","j+0","j+1","j+2"]
var polls={}
var echs={}
function getTsp(delta){
    //Init des dates (corrsepondances timestamp / runs)
    var date = new Date()
    var now =date.getTime()/1000
    var hours = date.getHours()
    var minutes = date.getMinutes()
    var secondes = date.getSeconds()
    var offset = (hours*3600+minutes*60+secondes)
    // pour se debarrasser de l'arrondi (qui donne parfois +1sec)
    tsp = (Math.round(Math.round(now-offset)/10)*10)-delta*86400
    //console.log(tsp)
    return tsp
}
today=getTsp(0)
yesterday=getTsp(1)
yyesterday=getTsp(2)


console.log(today,yesterday,yyesterday)
var runs={}
runs[today]=0
runs[yesterday]=1
runs[yyesterday]=2
// init des dates de j0 à j-2 pour afficher dans le tableau de droite
var jp0 = new Date(today*1000).toISOString().slice(5,10);
var jm1= new Date(yesterday*1000).toISOString().slice(5,10);
var jm2 = new Date(yyesterday *1000).toISOString().slice(5,10);
var dumb=0;


/* Création de la carte */
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

/* activation de la navigation simultanée, declenché par clic dans le menu */
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
//dict de l'ensemble de ssources retournées par la vue 'source_url' (redondant overlayersX ? à voire)
var liste_sources;
var prevs;
var active_poll_right_table;
///// --- init ----
//init successive de liste_source
//liste_source=[{
//      id : {
//      daterun : "15200220600",
//      ech:-1,
//      intrun : 0,
//      is_default_source: true,
//      pol:"PM10",
//      statut:true,
//      type:"ada",
//      url:"//home/vjulier/raster_...jm1_ada.tif",
//      __proto__ : Object}]
$.ajax({
    url: '{% url "init_today" '0' %}',
    async : false,
    success : function(msg){
        check_statut()       
    }
});
function check_statut() {
    $.ajax({
        url: '{% url "check_statut" %}',
        async : false,
        success : function(msg){
            //j=JSON.parse(msg)
            liste_sources=msg;
        }
    });
}

$.ajax({    
    url: '{% url "get_init_info"  %}',
    async: false,
    success : function(msg){
        //j=JSON.parse(msg)

        var k=Object.keys(msg)
        prevs=msg;
        buildLeftMenu()
        buildRightMenu()
    }
})    
/*         //construction du menu de droite
        //defaut sur PM10 adaptstat
        //reconstruit à chaque clic sur 
        var dic = getTypeDic('PM10','ada');
        buildTable(dic) */
function update_source(id_prev,id){
    id_but='lay_btn_'+id_prev.toString()
    overlayLayers1[id_but]=id
    $.ajax({
        url: '/raster/source/update_'+id_prev.toString()+'_'+id.toString(),
        success : function(msg){
            console.log(msg)
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
}
/* --------- DEBUT MAP-BLOCK1 ---------- */
/* Fonction de creation du menu de gestion des couches */
function buildLeftMenu() {
    var rll=$('#sidemenu > .raster-menu-left')
    for (i in prevs) {
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
    }   
    for (i in prevs) {
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
    }   

    layer_but_clic()
}

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
            // condition pour traiter les 2 map-block séparément
            if ($(this).closest("#map-block1").length == 1) {
                id_but=$(this)[0].id
                //null si on a pas encore initialisé (inutile si on affiche un polluant par defaut)
                if ( activeLayer1 != null) {
                    map.removeLayer(activeLayer1[1])
                }
                id_source = overlayLayers1[id_but]
                
                //workaround pour faire passer la variable id ds l'url
                url_img='{% url 'img_raster' id='0' %}'
                url_bbox='{% url 'bbox_raster' id='0' %}'

                img=url_img.slice(0,url_img.length-5)+id_source.toString()+'.png'
                bbox=url_bbox.slice(0,url_bbox.length-6)+id_source.toString()+'.json'
                console.log(bbox)
                console.log(img)

                // s1="'{% "
                // s2=" %}'"
                // s3=s1 + s + s2
                // console.log(s1 + s + s2)
                $.ajax({
                    //recup de scoins de la carte necessaires pour que leaflet affiche le png
                    url:bbox,
                    
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
            }
    });
};
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
            }
        }
    }
    dic=getTypeDic('PM10','ada')
    buildTable(dic)    
    active_poll_right_table="PM10";
}
function getTypeDic(poll,type){

    //reformate le liste source en un dictionnaire facilement utilisable pour construire le tableau
    //chaque ech (supporte pas les id negatif)
    var type_dic={0:{},1:{},2:{},3:{}};
    for (s in liste_sources) {      
        var obj=liste_sources[s]

        if ((obj.type==type) && (obj['pol']==poll)){            
            var ech=obj['ech']+1
            var tsp=obj['daterun']
            //console.log(tsp)
            run=runs[tsp]
            console.log(run)
            
            //console.log(run)
            type_dic[ech][run]=s;
           
        }
    }
    console.log(type_dic)
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
        for (run in type_dic[i]){
            //console.log(run)
            // pour inverser l'ordre des colonnes du tableaux :
            var reverse_ind =(run-2)*(-1)
            //console.log(reverse_ind)
            var id_source=type_dic[i][reverse_ind]
              
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
            active_poll_right_table=poll;
            if (poll!='MULTI'){
               
                var dic=getTypeDic(poll,'ada')
                buildTable(dic)
            }
            else {
                console.log('i_s_2')
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
        var dic=getTypeDic(poll,'')
        buildTable(dic)
    }
}
//gestion du clic sur le tableau de gestion des couches:
// - suppression de l'ancienne carte affichée
// - call de la nouvelle avec sa bounding box
// - maj de la variable activeLayer2
// function associée aux cases du tableau quand on le refresh
function td_clic() {
    $(".t2 > tbody > tr > td").click(function(){
        var id_source=($(this)[0].id).split("_")[1]
        o=liste_sources[id_source]
        $('#other_layers > a').remove()
        $('#other_layers > p').remove()
        $.ajax({
            url: "getMoreSources/"+id_source+".json",
            success : function(msg){
                //console.log(msg)
                var k=Object.keys(msg)
                $('#other_layers').append('<p>Autres sources pour le'+o.daterun+' à ' + lib_ech[o.ech+1] + '</p>')
                //on parse chaque source
                for (i=0;i<k.length;i++) {
                    //construction du menu de gauche (du map-block1)
                    var ind=k[i]
                    var ob=msg[ind]
                    //console.log(ind)
                    id_but='tr_'+ind.toString()
                    if (!(ob.type==o.type)){
                        var html_btn='<a href="#" class="list-group-item point-item other_layers"  id="'+id_but+'"> <h4 class="list-group-item-heading" >'+ob.type+'</h4>J ' + ob.ech.toString() + '    <span class="glyphicon glyphicon-chevron-right hide"></span><span class="badge">Ready</span></a>'
                        //console.log(ob)             
                        $('#other_layers').append(html_btn)
                        if (ob.statut!=true){
                            $("#"+id_but + "  > .badge").css("background-color","red")
                        }
                    }
                }
                other_layers_clic()
            }   
        })
        if (o.statut == false){
            alert('Pas de carte '+o.pol + ' disponible pour le '+ o.daterun + ', échéance à '+ lib_ech[o.ech+1] + ', source : ' + o.type + " (code couleur rouge). Si d'autres sources sont disponible pour ce run / échéance / polluant, elles s'afficheront en vers dans l'onglet \"autres sources\" qui apparait en cliquant sur uen case du tableau" )
        }
        else {
            if ( activeLayer2 != null) {
                map2.removeLayer(activeLayer2[1])
            }
            //workaround pour faire passer la variable id ds l'url
            url_img='{% url 'img_raster' id='0' %}'
            url_bbox='{% url 'bbox_raster' id='0' %}'
            
            
            img=url_img.slice(0,url_img.length-5)+id_source.toString()+'.png'
            bbox=url_bbox.slice(0,url_bbox.length-6)+id_source.toString()+'.json'
            console.log(img)
            $.ajax({
                url: bbox,
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
                }
            })
        }
        //console.log(url_bounds)
    })
};

function other_layers_clic() {
    $(".other_layers").click(function(){
        var id_source=($(this)[0].id).split("-")[2]
        
        if (liste_sources[id_source]['type']!='chim'){
            if ( activeLayer2 != null) {
                map2.removeLayer(activeLayer2[1])
            }
            var url="/raster/img/raster_"+id_source+".png";
            $.ajax({
                url: "/raster/bbox/raster_"+id_source+".json",
                success : function(msg){
                    var anchors = [
                        [msg['ymax'], msg['xmin']], //haut gauche
                        [msg['ymax'], msg['xmax']], //haut droite
                        [msg['ymin'], msg['xmax']], //bas droite
                        [msg['ymin'], msg['xmin']]  //bas gauche
                    ];
                    var lay = L.imageTransform(url, anchors,{opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});  
                    lay.addTo(map2)
                    activeLayer2=[id_source,lay];
                    console.log(id_source.toString())
                    var tbl=meta_source_tbl(liste_sources[id_source])
                    $('#active_layer_div2 > table').remove()
                    $('#active_layer_div2').append(tbl)
                }
            })
        }
        else if (liste_sources[id_source]['type']!='chim'){
            //TODO : comment faire pour la fine
        }
    })
        
}
/* --------- FIN DU MAP-BLOCK2 -------- */

function meta_source_tbl(obj){
    var tbl='<table class="table t_meta"><tbody><tr><th scope="row">Polluant : </th><td>'+obj.pol+'</td></tr><tr><th scope="row">Modèle : </th><td>'+obj.type+'</td></tr><tr><th scope="row">Date run </th><td>'+obj.daterun+'</td></tr><tr><th scope="row">Echeance </th><td>'+lib_ech[obj.ech+1]+'</td></tr></tbody></table>';
    console.log(tbl)
    return tbl
}
function switch_source() {
    if (activeLayer2==undefined){
        if (dumb >= 3){
            alert ('Pas de carte, pas de chocolat')
        }
        else {
            alert("Veuillez tout d'abord sélectionner une carte valide dans la fenêtre de droite")
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
        $('#switch_source_div').css('display','block')
        $("#new_source").append("<option value="+id_new_source+" selected disabled hidden>"+str_source+"</option>")
    }
}
function remove_switch_form() {
    $('#switch_source_div').css('display','none')
}
function validate_switch_btn(){
    id_prev=$("#switch_input > option:selected").val()
    id=$("#new_source > option:selected").val()
    console.log('id_prev : ' + id_prev)
    console.log('id : '+ id)
    update_source(id_prev,id)
}
function remove_multi_form() {
    $("#multi_div").hide()
    $("#mask").hide()
}
function calculate_multi(){
    $("tr > .td_valid > input:checked").each(function(i){
        i=parseInt($(this).attr('id').slice(-2))+1
        
        var url="/raster/img/raster_multi_"+i.toString()+".png";
        console.log(i)
        $.ajax({
            url: url
            ,success : function(){
                console.log('success multi => a check')
                refresh_right_table()
            }
        })
    })
    $("#mask").hide()
    $("#multi_div").hide()
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
                overlayButId="lay_btn_"+i.toString()
                id_source=overlayLayers1[overlayButId]
                src=liste_sources[id_source ]
                lib=lib_ech[ech+1].toString()
                id_row='tr_'+ech.toString()+"_"+pol.toLowerCase()

                $("#"+id_row+" > .td_poll_source").text(src['pol'])
                $("#"+id_row+" > .td_type").text(src['type'])
                $("#"+id_row+" > .td_date").text(src['daterun'])
                $("#"+id_row+" > .td_ech_source").text(src['ech'])
                
            }
        }
    }
                                            // <td class="td_poll_prev">O3</td>
                                        // <td class="td_poll_source"></td>
                                        // <td class="td_type"></td>
                                        // <td class="td_date"></td>
                                        // <td class="td_ech_source"></td>
        // $(".t2 > thead").remove()
    // $(".t2 > tbody").remove()
    // $(".t2").append("<thead class='thead-inverse'><tr><th></th><th>"+jm2+"</th><th>"+jm1+"</th><th>"+jp0+"</th><tr></thead>")
    // $(".t2").append("<tbody></tbody>")
    // for (i in type_dic){
        // $(".t2 > tbody").append("<tr id='tr_"+i.toString()+"'><th scope='row'>"+(i-1).toString()+"</th></tr>")
                                    // <th rowspan="3" scope="row">-1</th>
                                        // <td class="red not_source" id="run_tty1310"></td>
                                        // <td class="red not_source" id="run_1ty258"></td>
                                        // <td class="red not_source" id="run_1y206"></td>
                                        // <td class="red not_source" id="run_tty1310"></td>
                                        // <td class="red not_source" id="run_1ty258"></td>
                                        // <td class="red not_source" id="run_1y206"></td>
                                        // <td rowspan="3" class="red not_source" id="run_1zery206"><input id="checkBox" type="checkbox"></td>
}



/* Chargement du fond de carte */
// comme toutes les couches, on est obligé de l'instancier une fois par objet map...
var mapbox_light = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoicmh1bSIsImEiOiJjaWx5ZmFnM2wwMGdidmZtNjBnYzVuM2dtIn0.MMLcyhsS00VFpKdopb190Q', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.light',
    opacity: 1.,
});   
mapbox_light.addTo(map);
var mapbox_light2 = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoicmh1bSIsImEiOiJjaWx5ZmFnM2wwMGdidmZtNjBnYzVuM2dtIn0.MMLcyhsS00VFpKdopb190Q', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.light',
    opacity: 1.,
});   
mapbox_light2.addTo(map2);


/* Déclaration de l'emprise max */
/* var  bounds = new L.LatLngBounds( 
   new L.LatLng(44.1154926129760483, 2.0628781476760838), // SW  L.LatLng(42.92986796194353,4.220712166125205)
   new L.LatLng(46.8042870493686962, 7.1855613116475361)  // NE  L.LatLng(45.17322865209258,7.804443841248857)
);
map.fitBounds(bounds); */
//2.0628781476760838,44.1154926129760483 : 7.1855613116475361,46.8042870493686962


//fonction popup sur champ 'nom'
//utilisé par les couches vecteurs
function onEachFeature(feature, layer) {
        var popupContent="";
        if (feature.properties && feature.properties.nom) {
            popupContent += feature.properties.nom;
        }

        layer.bindPopup(popupContent);
    }

// Enregistrement du polluant et de l'échéance par defaut



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
/* var epci_aura;
$.ajax({
    url: '{% url "epci_aura"  %}',
    success : function(msg){
        //j=JSON.parse(msg)
        

        epci_aura = L.geoJSON(
            msg,
            {
                onEachFeature: onEachFeature,
                style: function(feature) {
                     return {
                        color : "#000000",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0
                    }
                }
            }
        )

        vectorLayers['epci_aura']= {'objet' : epci_aura}
                //clone grace au plugin clonelayer pour permettre d'afficher sur les 2 frames
        var  epci_aura_2 = cloneLayer(epci_aura);
        vectorLayers['epci_aura_2']= {'objet' : epci_aura_2}
        setTimeout(console.log(vectorLayers),20000)
        
    }
}); */
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
/*cacher les onglets fine échelle au clic sur la croix*/
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


/* Fonctions éxecutées on click */
map.on('click', function(e) {   
    val=''
    coords = e.latlng;
    console.log(coords)
    if (activeLayer1===undefined){
        console.log("pas de carte affichée... pas de carte... pas de concentration")
    }
    else {
        id_source=activeLayer1[0]
        url='{% url 'get_pixel' id='0' x='0' y='0' %}'
        url2='/raster/api/pixel_'+id_source.toString()+'_'+Math.round(coords['lng']*1000000).toString()+'_'+Math.round(coords['lat']*1000000).toString()
        console.log(url)
        $.ajax({

            url:url2,
            success : function(msg){
                //j=JSON.parse(msg)
                console.log(msg)
                //les cles du dic 'liste_source' sont l'id de la source
                var k=Object.keys(msg)

            }
        });
    }

});    
map2.on('click', function(e) {   
    val=''
    coords = e.latlng;
    console.log(coords)
    if (activeLayer2===undefined){
        console.log("pas de carte affichée... pas de carte... pas de concentration")
    }
    else {
        id_source=activeLayer2[0]
        url='{% url 'get_pixel' id='0' x='0' y='0' %}'
        url2='/raster/api/pixel_'+id_source.toString()+'_'+Math.round(coords['lng']*1000000).toString()+'_'+Math.round(coords['lat']*1000000).toString()
        console.log(url)
        $.ajax({

            url:url2,
            success : function(msg){
                //j=JSON.parse(msg)
                console.log(msg)
                //les cles du dic 'liste_source' sont l'id de la source
                var k=Object.keys(msg)

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
        circle: false,
        polyline: false,
        rectangle: false,
    },
    position: 'topleft'
}));

// Action après dessin
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
    ($('#corr_form_type'))[0][0].value = "Gaussienne - " + type;
    ($('#corr_form_type'))[0][0].innerText = "Gaussienne - " + type;
    
    /* Ajout de l'élément crée au groupe */
    drawnItems.addLayer(layer);
});

// Action après modification de forme
map.on('draw:edited', function (event) {
    var layers = event.layers;
    layers.eachLayer(function (layer) {
    
        // Afficher le formulaire d'insertion
        $('#modal_corr_form').modal('show');
        
    });
});

/* Fonction éxécutée lors de l'envoi du formulaire de correction */ 
$("#submitFormCorr").click(function (e) {
    console.log("envoi");
    
    e.preventDefault();

    var corr_type = ($('#corr_form_type'))[0].value;
    var corr_value = ($('#corr_form_val'))[0].value;
    var corr_min = ($('#corr_form_min'))[0].value;
    var corr_max = ($('#corr_form_max'))[0].value;
    var corr_ssup = ($('#corr_form_ssup'))[0].value;
    var id_source=activeLayer1[0]
    console.log("Vérification du formulaire");

    /* Vérification du formulaire */   
    if (corr_coords == "" || corr_coords == 'undefined' || corr_coords == []) {
        console.log("Erreur verif formulaire: coords");
        $("#error_tube").show(); // FIXME: Pas crée
        return;
    };
    if (corr_value == "" || corr_value == 'undefined') {
        console.log("Erreur verif formulaire: valeur");
        $("#error_tube").show(); // FIXME: Pas crée
        return;
    };
    if (corr_min == "" || corr_min == 'undefined' || corr_min == []) {
        console.log("Erreur verif formulaire: min : set min = 0");
        corr_min=0
        //$("#error_tube").show(); // FIXME: Pas crée

    };
    if (corr_max == "" || corr_max == 'undefined' || corr_max == []) {
        console.log("Erreur verif formulaire: max : set max = 9999");
        corr_max=9999
        //$("#error_tube").show(); // FIXME: Pas crée

    };
    if (corr_ssup == "" || corr_ssup == 'undefined' || corr_ssup == []) {
        console.log("Erreur verif formulaire: seuil sup : set ssup = 9999");
        corr_ssup=9999
        //$("#error_tube").show(); // FIXME: Pas crée

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
    var csrftoken = getCookie('csrftoken');
    console.log(csrftoken);
    $.ajaxSetup({   headers: {  "X-CSRFToken": csrftoken  }  });

    console.log(corr_coords)
    var wkt = $.geo.WKT.stringify( {
        type: 'Polygon',
        coordinates: [corr_coords,[]]
    } );
    console.log(wkt)
    // Execution de la transaction Ajax - Page JV
    $.ajax({
        type: "POST",

        headers: { "X-CSRFToken": csrftoken },
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
               
            //null si on a pas encore initialisé (inutile si on affiche un polluant par defaut)
            if ( activeLayer1 != null) {
                map.removeLayer(activeLayer1[1])
            }
            id_source = overlayLayers1[id_but]
            
            //workaround pour faire passer la variable id ds l'url
            url_img='{% url 'img_raster' id='0' %}'
            url_bbox='{% url 'bbox_raster' id='0' %}'

            img=url_img.slice(0,url_img.length-5)+id_source.toString()+'.png'
            bbox=url_bbox.slice(0,url_bbox.length-6)+id_source.toString()+'.json'
            console.log(bbox)
            console.log(img)

            // s1="'{% "
            // s2=" %}'"
            // s3=s1 + s + s2
            // console.log(s1 + s + s2)
            $.ajax({
                //recup de scoins de la carte necessaires pour que leaflet affiche le png
                url:bbox,
                
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
 
}); 

/* Fonction éxécutée lors de l'annulation de l'envoi du formulaire de correction */
$("#reset").click(function (e) {
    console.log("Annulation de l'envoie, on conserve l'objet pour éventuelles modifications.")
});

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
}
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function test(){
    console.log('iug')
    $.ajax({
        type: "POST",
        //csrfmiddlewaretoken: '{{ csrf_token }}',
        headers: { "X-CSRFToken": getCookie("csrftoken") },
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
