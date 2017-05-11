/* Variables globales pour stocker les paramètres de correction */
var corr_pollutant = "";
var corr_echeance = "";
var corr_type = "";
var corr_coords = [];
var corr_value = "";

/* Création de la carte */
var map = L.map('map', { zoomControl:false }, {layers: []}).setView([43.9, 6.0], 8);    
map.attributionControl.addAttribution('CARINE v3 &copy; AIR PACA - 2017</a>'); 

/* Chargement du fond de carte */
var mapbox_light = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoicmh1bSIsImEiOiJjaWx5ZmFnM2wwMGdidmZtNjBnYzVuM2dtIn0.MMLcyhsS00VFpKdopb190Q', {
    maxZoom: 18,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.light',
    opacity: 1.,
});   
// mapbox_light.addTo(map);

var Hydda_Full = L.tileLayer('http://{s}.tile.openstreetmap.se/hydda/full/{z}/{x}/{y}.png', {
	maxZoom: 18,
	attribution: 'Tiles courtesy of <a href="http://openstreetmap.se/" target="_blank">OpenStreetMap Sweden</a> &mdash; Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});
Hydda_Full.addTo(map);

/* Déclaration de l'emprise max */
var	bounds = new L.LatLngBounds( 
    new L.LatLng(42.9374, 3.52073), // SW  L.LatLng(42.92986796194353,4.220712166125205)
    new L.LatLng(44.0938, 7.54861)  // NE  L.LatLng(45.17322865209258,7.804443841248857)
);
map.fitBounds(bounds);

/* Ajout des cartes de prévi */
var anchors = [
    [44.0938, 4.22073],	//haut gauche
    [44.0938, 7.54888],	//haut droite
    [42.9363, 7.54888],	//bas droite
    [42.9363, 4.22073] 	//bas gauche
];

var layer_no2jm1 = L.imageTransform("{% url 'img_raster' pol='NO2' ech=-1 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_no2jp0 = L.imageTransform("{% url 'img_raster' pol='NO2' ech=0 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_no2jp1 = L.imageTransform("{% url 'img_raster' pol='NO2' ech=1 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_no2jp2 = L.imageTransform("{% url 'img_raster' pol='NO2' ech=2 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_pm10jm1 = L.imageTransform("{% url 'img_raster' pol='PM10' ech=-1 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_pm10jp0 = L.imageTransform("{% url 'img_raster' pol='PM10' ech=0 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_pm10jp1 = L.imageTransform("{% url 'img_raster' pol='PM10' ech=1 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});
var layer_pm10jp2 = L.imageTransform("{% url 'img_raster' pol='PM10' ech=2 %}", anchors, {opacity:0.7, attribution: 'Cartes de pollution: airpaca'});

/* Affichage d'origine */
layer_no2jp0.addTo(map);	

/* Ajout des couches dans un dictionnaire des couches */
var baseLayers = {
    'mapbox_light': mapbox_light,
};
var overlayLayers = {
    'layer_no2jm1': {"objet": layer_no2jm1, "polluant": "no2", "echeance": "j-1"},
    'layer_no2jp0': {"objet": layer_no2jp0, "polluant": "no2", "echeance": "j+0"},
    'layer_no2jp1': {"objet": layer_no2jp1, "polluant": "no2", "echeance": "j+1"},
    'layer_no2jp2': {"objet": layer_no2jp2, "polluant": "no2", "echeance": "j+2"},
    'layer_pm10jm1': {"objet": layer_pm10jm1, "polluant": "pm10", "echeance": "j-1"},
    'layer_pm10jp0': {"objet": layer_pm10jp0, "polluant": "pm10", "echeance": "j+0"},
    'layer_pm10jp1': {"objet": layer_pm10jp1, "polluant": "pm10", "echeance": "j+1"},
    'layer_pm10jp2': {"objet": layer_pm10jp2, "polluant": "pm10", "echeance": "j+2"},
};

// Enregistrement du polluant et de l'échéance par defaut
var corr_pollutant = "no2";
var corr_echeance = "pm10";

/* Fonction de gestion des couches */
$(function() {
    $('.list-group-item').click( function() {
        
        /* Gestion de la liste des couches */
        
        // Boutons actifs
        $(this).addClass('active').siblings().removeClass('active');
        
        if ($(this).closest('div').attr('id') == "no2"){
            $("#pm10 a").removeClass('active');
        };
        if ($(this).closest('div').attr('id') == "pm10"){
            $("#no2 a").removeClass('active');
        };        

        // Chevrons
        $("a .glyphicon-chevron-right").addClass('hide');		
        $("#" + $(this)[0].id + " .glyphicon-chevron-right").removeClass('hide');
    
        // // légendes
        // $("[class*=lgd_]").addClass('hide');	
        // $("." + $(this)[0].id.replace("layer", "lgd")).removeClass('hide'); 
        
    
        /* Gestion de l'affichage des couches */
        
        // Suppression des couches actives
        for (alayer in overlayLayers) {
            if (!($(this)[0].id == alayer)){
                map.removeLayer(overlayLayers[alayer]["objet"]);
            };
        };		
        
        // Ajout de la couche choisie
        overlayLayers[$(this)[0].id]["objet"].addTo(map);
        
        // Récupération du polluant et de l'échéance en cours d'utilisation
        corr_pollutant = overlayLayers[$(this)[0].id]["polluant"];
        corr_echeance = overlayLayers[$(this)[0].id]["echeance"];

    });
});	

/* Fonctions éxecutées on click */
map.on('click', function(e) {   
    corr_coords = e.latlng;
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
            type: 'point',
            delta: 5,
            lon: 6,
            lat: 45  
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

