// Function to generate a slug from a name
function generateSlug(name) {
    return name.toLowerCase()
               .replace(/ /g, '-') // Replace spaces with dashes
               .replace(/[^\w-]+/g, ''); // Remove all non-word characters
}

// Function to extract the borough from a place object
function getBoroughFromPlace(place) {
    for (const component of place.address_components) {
        if (component.types.includes("sublocality") || component.types.includes("neighborhood")) {
            return component.long_name;
        }
    }
    return null;
}

// Function to get the postal town from the place object
function getPostalTown(place) {
    if (!place.address_components) {
        return null;
    }
    for (let component of place.address_components) {
        if (component.types.includes("postal_town")) {
            return component.long_name;
        }
    }
    return null;
}

// Get post code
function getPostcodeFromPlace(place) {
    if (!place || !place.address_components) {
      return null;
    }
    for (let i = 0; i < place.address_components.length; i++) {
      const component = place.address_components[i];
      if (component.types.includes("postal_code")) {
        return component.long_name;
      }
    }
    return null;
  }  

// Extract Address 1
function getTextBeforeLondonPostcode(address) {
    const londonPostcodePattern = /, London\s+[A-Z]{1,2}[0-9R][0-9A-Z]? ?[0-9][A-Z]{2}/;
    const match = address.match(londonPostcodePattern);
    if (match) {
        // Get the start index of the pattern
        const patternIndex = address.indexOf(match[0]);
        // Extract the text before the pattern
        const textBeforePattern = address.substring(0, patternIndex);
        return textBeforePattern.trim();  // Remove any trailing spaces
    } else {
        return address;
    }
}

var savePath;

function downloadImage(url, name, id) {
    fetch('/download_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url, name: name, id: id })
    })
    .then(response => response.json())
    .then(data => {
        savePath = data.path;
        console.log(data.message);
        console.log("Save Path:", savePath);

        // Update the hidden input element with the new save path
        var inputElement = document.getElementById('place_img_url');
        if (inputElement) {
            inputElement.value = savePath;
            console.log('Changed thumbnail input value');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Initialize a global variable to store the place name
var globalPlaceName = '';

// Suggest page script
function initMap() {
    var map = new google.maps.Map(document.getElementById('geocomplete-map'), {
        center: { lat: 51.5074, lng: -0.1278 }, // London coordinates
        zoom: 10,
    });

    var marker = new google.maps.Marker({
        map: map,
        visible: false // Initially hide the marker
    });

    var londonBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(51.28676, -0.510375), // South West coordinates of London
        new google.maps.LatLng(51.691874, 0.334015)  // North East coordinates of London
    );

    var autocomplete = new google.maps.places.Autocomplete(document.getElementById('geocomplete'), {
        types: ['establishment'], // Restrict autocomplete to specific types of locations
        bounds: londonBounds // Restrict autocomplete to London bounds
    });

    autocomplete.addListener('place_changed', function () {
        var place = autocomplete.getPlace();

        fetch(`/api/check_cafe?place_id=${place.place_id}`)
            .then(response => response.json())
            .then(data => {
                var stepExists = document.getElementById('step_exists');
                var nextButton = document.getElementById('nextButton');
                var retryButton = document.getElementById('retryButton');
                var cafeLink = document.getElementById('cafeLink');

                if (data.exists) {
                    stepExists.style.display = 'block';
                    nextButton.style.display = 'none';
                    retryButton.style.display = 'block';

                    // Construct the URL for the cafe
                    var url = showCafeUrlBase
                        .replace('LOCATION_PLACEHOLDER', `${data.location_slug}`)
                        .replace('CAFE_PLACEHOLDER', `${data.cafe_slug}`)
                        .replace('ID_PLACEHOLDER', `${data.id}`);

                    console.log(url)

                    cafeLink.href = url;
                    return;
                } else {
                    stepExists.style.display = 'none';
                    nextButton.style.display = 'block';
                    retryButton.style.display = 'block';
                }

                const postalTown = getPostalTown(place);
                if (!postalTown) {
                    alert("Error, please choose a different location in London.");
                    return;
                } else if (postalTown !== "London") {
                    alert("Location not found in London.");
                    return;
                }

                var step2 = document.getElementById('step2');
                var controls = document.getElementById('controls');

                step2.style.display = '';
                controls.style.display = '';
                nextButton.style.display = 'block';
                retryButton.style.display = 'block';

                if (!place.geometry || !place.geometry.location) {
                    return;
                }

                map.setCenter(place.geometry.location);
                map.setZoom(17);

                marker.setPosition(place.geometry.location);
                marker.setVisible(true);

                var photos = place.photos;
                if (photos) {
                    var photoUrls = photos.map(function (photo) {
                        return photo.getUrl({ maxWidth: 2500, maxHeight: 2500 });
                    });

                    generateImageGrid(photoUrls, place.name, place.place_id);
                }

                autofillLocationInfo(place);

                globalPlaceName = place.name;
            })
            .catch(error => console.error('Error:', error));
    });

    function autofillLocationInfo(place) {
        var inputElement;

        inputElement = document.getElementById('place_name');
        if (inputElement) {
            inputElement.value = place.name;
        }
        inputElement = document.getElementById('place_location_address');
        if (inputElement) {
            inputElement.value = getTextBeforeLondonPostcode(place.formatted_address);
        }
        inputElement = document.getElementById('place_location_postal_code');
        if (inputElement) {
            inputElement.value = getPostcodeFromPlace(place);
        }
        inputElement = document.getElementById('place_google_place_gid');
        if (inputElement) {
            inputElement.value = place.place_id;
        }
        inputElement = document.getElementById('place_location_lat');
        if (inputElement) {
            inputElement.value = place.geometry.location.lat();
        }
        inputElement = document.getElementById('place_location_lng');
        if (inputElement) {
            inputElement.value = place.geometry.location.lng();
        }
        inputElement = document.getElementById('place_borough');
        if (inputElement) {
            inputElement.value = getBoroughFromPlace(place);
        }
        inputElement = document.getElementById('place_weekday_text');
        if (inputElement) {
            inputElement.value = place.opening_hours.weekday_text;
        }
    }

    function selectThumbnail(thumbnailDiv, photoUrl, name, id) {
        var prevSelectedThumbnail = document.querySelector('.thumbnails.image_picker_selector .thumbnail.selected');
        if (prevSelectedThumbnail) {
            prevSelectedThumbnail.classList.remove('selected');
        }
        thumbnailDiv.classList.add('selected');
        console.log("Selected photo:", photoUrl);
        downloadImage(photoUrl, name, id);
    }

    function generateImageGrid(photoUrls, name, id) {
        var imageGrid = document.querySelector('.thumbnails.image_picker_selector');
        imageGrid.innerHTML = '';

        var maxImages = Math.min(photoUrls.length, 6);

        for (var i = 0; i < maxImages; i++) {
            var listItem = document.createElement('li');

            var thumbnailDiv = document.createElement('div');
            thumbnailDiv.className = 'thumbnail';

            var img = document.createElement('img');
            img.className = 'image_picker_image';
            img.src = photoUrls[i];

            thumbnailDiv.addEventListener('click', (function (index) {
                return function () {
                    selectThumbnail(this, photoUrls[index], name, id);
                };
            })(i));

            thumbnailDiv.appendChild(img);
            listItem.appendChild(thumbnailDiv);
            imageGrid.appendChild(listItem);
        }

        var firstThumbnail = imageGrid.querySelector('.thumbnail');
        if (firstThumbnail) {
            selectThumbnail(firstThumbnail, photoUrls[0], name, id);
        }

        imageGrid.style.display = 'block';
    }
}

window.onload = function () {
    initMap();
};












// function initialize() {
//     var input = document.getElementById('geocomplete'); // Targeting the input field by its ID
//     var autocomplete = new google.maps.places.Autocomplete(input, {
//         types: ['establishment']  // Restrict autocomplete to specific types of locations
//     });
//     var form = document.getElementById('search_location');
        
//             google.maps.event.addListener(autocomplete, 'place_changed', function() { // place_changed triggers our function when a place is selected from the suggestions dropdown
//                 var place = autocomplete.getPlace();
        
//                 // Set the value for the hidden input field
//                 document.getElementById('place').value = JSON.stringify(place);
        
        
//                 // Submit the form programmatically
//                 form.submit();

    // google.maps.event.addListener(autocomplete, 'place_changed', function() { // place_changed triggers our function when a place is selected from the suggestions dropdown
    //     var place = autocomplete.getPlace();
    //     var location = place.name;
    //     var latitude = place.geometry.location.lat();
    //     var longitude = place.geometry.location.lng();

        // console.log('Location:', location);
        // console.log('Latitude:', latitude);
        // console.log('Longitude:', longitude);

        // fetch('/suggest', {
        //     method: 'POST',
        //     body: new URLSearchParams({ 'location': location,'latitude': latitude,
        //     'longitude': longitude }),
        //     headers: {
        //         'Content-Type': 'application/x-www-form-urlencoded'
        //     }
        // })
        // .then(response => response.text())
        // .then(data =>console.log(data))
        // // .then(data => {
        // //     document.getElementById('result').innerHTML = data;
        // // })
        // .catch(error => console.error('Error:', error));
//     });
// }
// google.maps.event.addDomListener(window, 'load', initialize);
