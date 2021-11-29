var circleClusterremove = [];
        var buffer_circle = null;
        // To load google map
        function initialize() {
            var mapOptions = {
                center: new google.maps.LatLng(-23.5668287,-46.6549423),
                zoom: 12,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
            map.setMapTypeId(google.maps.MapTypeId.ROADMAP);

            new google.maps.Marker({
                position: new google.maps.LatLng(-23.5668287,-46.6549423),
                map,
                title: "Sua Empresa Aqui",
             });



        }
        // set onclick listener to pick a location on map
        function setListenerBuffer() {
            map.setOptions({ draggableCursor: 'crosshair' });
            google.maps.event.addListenerOnce(map, "click", function (latlng) {
                map.setOptions({ draggableCursor: '' });
                createCircle(latlng.latLng);
            });
            return false;
        }
        // Draw circle with in radius
        function createCircle(cntr) {
            var rad = parseInt($("#StRaio").val())*1000

            if (buffer_circle != null) {
                buffer_circle.setMap(null);
            }
            buffer_circle = new google.maps.Circle({
                center: cntr,
                radius: rad,
                strokeColor: "",
                strokeOpacity: 0.0,
                strokeWeight: 2,
                fillColor: "#FFD700",
                fillOpacity: 0.5,
                map: map
            });
            circleClusterremove.push(buffer_circle);
        }
        // To remove circle from google map
        function RemoveCircleBuffer() {
            try {
                for (var i = 0; i < circleClusterremove.length; i++) {
                    circleClusterremove[i].setMap(null);
                }
                circleClusterremove = [];
            }
            catch (Error) {
            }
        }