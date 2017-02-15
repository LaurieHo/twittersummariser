//create empty map
var map = L.map('map');
map.setView([50.5, -25.0], 2); //set map centre and initial zoom

//tile images from OpenStreetMap
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);



// Read the geodata with jQuery and add tweet locations as dots on the map
$.getJSON("/static/geo_data.json", function(data) {
    var myStyle = {
        radius: 2,
        fillColor: "red",
        color: "red",
        weight: 1,
        opacity: 1,
        fillOpacity: 1
    };
 
    var geojson = L.geoJson(data, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, myStyle);
        }
    });
    geojson.addTo(map)
});

