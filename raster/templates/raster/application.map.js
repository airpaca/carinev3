/* Variables globales pour stocker les paramètres de correction */
var corr_pollutant = "";
var corr_echeance = "";
var corr_type = "";
var corr_coords = [];
var corr_value = "";

// init des dates de j0 à j-2 pour afficher dans le tableau de droite
var date = new Date()
var jp0 = date.toISOString().slice(5,10);
date.setDate(date.getDate()-1)
var jm1= date.toISOString().slice(5,10);
date.setDate(date.getDate()-1)
var jm2 = date.toISOString().slice(5,10);


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


///// --- init ----
//init successive de :
//liste_source
//liste_source={
//		id : {
//		daterun : "18_07_2017",
// 		ech:-1,
//		intrun : 0,
//		is_default_source: true,
//		pol:"PM10",
//		statut:true,
//		type:"ada",
//		url:"//home/vjulier/raster_...jm1_ada.tif",
//		__proto__ : Object}


$.ajax({
	url: '{% url "source_url"  %}',
	success : function(msg){
		//j=JSON.parse(msg)
		console.log(msg)
		liste_sources=msg;
		//construction du menu de gauche
		build_left_menu(msg)
		
		//construction du menu de droite
		//defaut sur PM10 adaptstat
		//reconstruit à chaque clic sur 
		var dic = getTypeDic('PM10','ada');
		buildTable(dic)
	}
});

/* --------- DEBUT MAP-BLOCK1 ---------- */
/* Fonction de creation du menu de gestion des couches */
function build_left_menu(msg) {
	
	//les cles du dic 'liste_source' sont l'id de la source
	var k=Object.keys(msg)
	//on parse chaque source
	for (i=0;i<k.length;i++) {
		//construction du menu de gauche (du map-block1)
		var ind=k[i]
		var ob=msg[ind]
		if (ob.is_default_source==true){

			var id_but='lay_btn_'+ind.toString()
			var cls=ob.pol.toLowerCase()		
			var html_btn='<a href="#" class="list-group-item point-item baselayer"  id="'+id_but+'"> <h4 class="list-group-item-heading" >'+ob.pol+'</h4>J ' + ob.ech.toString() + '    <span class="glyphicon glyphicon-chevron-right hide"></span><span class="badge">Ready</span></a>'
			overlayLayers1[id_but]={'id_source' :  ind , 'obj' : ob}
			var sel='#sidemenu > .' + cls
			$(sel).append(html_btn)
			if (ob.statut!=true){
				$("#"+id_but + "  > .badge").css("background-color","red")
			}
		}
	}
	layer_but_clic()
}
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
					map.removeLayer(activeLayer1)
				}
				id_source = overlayLayers1[id_but].id_source
				url="/raster/img/raster_"+id_source+".png";
				console.log(url)
				$.ajax({
					//recup de scoins de la carte necessaires pour que leaflet affiche le png
					url: "/raster/bbox/raster_"+id_source+".json",
					success : function(msg){
						anchors = [
							[msg['ymax'], msg['xmin']],	//haut gauche
							[msg['ymax'], msg['xmax']],	//haut droite
							[msg['ymin'], msg['xmax']],	//bas droite
							[msg['ymin'], msg['xmin']] 	//bas gauche
						];
						lay = L.imageTransform(url, anchors, {opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});		
						lay.addTo(map)
						activeLayer1=lay;
					}
				})	
			}
	});
};
/* ---------- FIN MAP-BLOCK1 ------------ */


/* ------ DEBUT MAP-BLOCK2 ------ */
function getTypeDic(poll,type){
	//reformate le liste source en un dictionnaire facilement utilisable pour construire le tableau
	//chaque ech (supporte pas les id negatif)
	var type_dic={0:{},1:{},2:{},3:{}};
	for (s in liste_sources) {		
		var obj=liste_sources[s]
		//console.log(obj)
		if ((obj.type==type) && (obj['pol']==poll)){			
			var ech=obj['ech']+1
			var run=obj['intrun']
			type_dic[ech][run]=s;
		}
	}
	return type_dic;
}
function buildTable(type_dic){
	//TODO : a mettre dynamique selon  les polluants echeances etc.. (pas urgent ceci dit..)
	$(".table > thead").remove()
	$(".table > tbody").remove()
	$(".table").append("<thead class='thead-inverse'><tr><th></th><th>"+jm2+"</th><th>"+jm1+"</th><th>"+jp0+"</th><tr></thead>")
	$(".table").append("<tbody></tbody>")
	for (i in type_dic){
		$(".table > tbody").append("<tr id='tr_"+i.toString()+"'><th scope='row'>"+(i-1).toString()+"</th></tr>")
		for (run in type_dic[i]){
			//console.log(run)
			// pour inverser l'ordre des colonnes du tableaux :
			var reverse_ind =(run-2)*(-1)
			//console.log(reverse_ind)
			var id_source=type_dic[i][reverse_ind]
			//console.log(id_source)
			
			var col='red';	
			if (liste_sources[id_source].statut==true){
				col='green'
			}
			var is_source='not_source'
			for (id_but in overlayLayers1){
				//console.log(overlayLayers1[id_but]['id_source'])
				if (overlayLayers1[id_but]['id_source']==id_source){
					is_source='yes_source'	
				}
			}
			$("#tr_" + i.toString()).append("<td class='"+col+" "+is_source+"' id=run_"+id_source+"></td>")
		}	
	}
	td_clic()
}

//on reconstruit le tableau de gestion des couches si on change de polluant
$(function() {
	$("#poll_switch_2 > .NO2").click(			
		function(){
			var dic=getTypeDic("NO2",'ada')
			buildTable(dic)
		}
	)	
});
$(function() {
	$("#poll_switch_2 > .O3").click(			
		function(){
			var dic=getTypeDic("O3",'ada')
			buildTable(dic)
		}
	)	
});
$(function() {
	$("#poll_switch_2 > .PM10").click(			
		function(){
			var dic=getTypeDic("PM10",'ada')
			buildTable(dic)
		}
	)	
});
//gestion du clic sur le tableau de gestion des couches:
// - suppression de l'ancienne carte affichée
// - call de la nouvelle avec sa bounding box
// - maj de la variable activeLayer2
// function associée aux cases du tableau quand on le refresh
function td_clic() {
	$(".table > tbody > tr > td").click(function(){
		if ( activeLayer2 != null) {
			map2.removeLayer(activeLayer2)
		}
		var id_source=($(this)[0].id).substr(-3,3)
		var url="/raster/img/raster_"+id_source+".png";
		$.ajax({
			url: "/raster/bbox/raster_"+id_source+".json",
			success : function(msg){
				var anchors = [
					[msg['ymax'], msg['xmin']],	//haut gauche
					[msg['ymax'], msg['xmax']],	//haut droite
					[msg['ymin'], msg['xmax']],	//bas droite
					[msg['ymin'], msg['xmin']] 	//bas gauche
				];
				var lay = L.imageTransform(url, anchors,{opacity:0.7, attribution: 'Cartes de pollution: ATMO Aura'});	
				lay.addTo(map2)
				activeLayer2=lay;
			}
		})
		//console.log(url_bounds)
	})
};
/* --------- FIN DU MAP-BLOCK2 -------- */


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
/* var	bounds = new L.LatLngBounds( 
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
var corr_pollutant = "no2";
var corr_echeance = "pm10";


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
    coords = e.latlng;
	console.log(coords)
});    
map2.on('click', function(e) {   
    coords = e.latlng;
	console.log(coords)
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
        corr_coords.push(layer._latlng.lat, layer._latlng.lng);
    };		

    if (type === 'polygon') {
    
        corr_coords = [];
        for (var point in layer._latlngs[0]) {
            corr_coords.push([layer._latlngs[0][point].lat, layer._latlngs[0][point].lng]);
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
    
    console.log("Vérification du formulaire");
   
    /* Vérification du formulaire */
    if (corr_pollutant == "" || corr_pollutant == 'undefined') {
        console.log("Erreur verif formulaire: polluant");
        $("#error_tube").show(); // FIXME: Pas crée
        return;
    };
    if (corr_echeance == "" || corr_echeance == 'undefined') {
        console.log("Erreur verif formulaire: echéance");
        $("#error_tube").show(); // FIXME: Pas crée
        return;
    };        
    if (corr_type == "" || corr_type == 'undefined') {
        console.log("Erreur verif formulaire: type");
        $("#error_tube").show(); // FIXME: Pas crée
        return;
    };
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
    
    console.log("***********************");
    console.log("Submission du formulaire de correction:");
    console.log("Polluant: " + corr_pollutant);
    console.log("Echéance: " + corr_echeance);
    console.log("Type: " + corr_type); 
    console.log("Coords: " + corr_coords); 
    console.log("Valeur: " + corr_value);
    console.log("***********************");
    
/*     // Execution de la transaction Ajax
    $.ajax({
        type: "POST",
        url: "reception_formulaire.php", // "reception_formulaire.php",
        data: { 
            polluant: corr_pollutant, 
            echeance: corr_echeance,
            type: corr_type,
            coords: corr_coords,
            value: corr_value
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
            
            // Fermeture du formulaire 
            $("#modal_corr_form").modal('hide'); 				
            
        },
        error: function (request, error) {
            console.log("ERROR");
            console.log(arguments);
            console.log("Ajax error: " + error);
            $("#error_tube").show();
        },        
    });	 */
    
    
    // Execution de la transaction Ajax - Page JV
    $.ajax({
        type: "POST",
        // crossDomain : true,
        // headers:{ 'Access-Control-Allow-Origin':'http://vmli-grass:5100/alter/raster', 'Access-Control-Allow-Headers': 'x-requested-with' },
        url: "{% url 'alter_raster' %}",
        data: { 
            // polluant: corr_pollutant, 
            // echeance: corr_echeance,
            // type: corr_type,
            // coords: corr_coords,
            // value: corr_value    
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
            
            // Fermeture du formulaire 
            $("#modal_corr_form").modal('hide'); 				
            
        },
        error: function (request, error) {
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

