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

// Initialize a global variable to store the place name
var globalPlaceName = '';

// Suggest page script
function initMap() {
    var map = new google.maps.Map(document.getElementById('geocomplete-map'), {
        center: { lat: 51.5074, lng: -0.1278 }, // London coordinates
        zoom: 10,
    });

    // Initialize the marker (initially hidden)
    var marker = new google.maps.Marker({
        map: map,
        visible: false // Initially hide the marker
    });

    // Define the bounds for London (restricts autocomplete to only show locations in London)
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

        // Set the value of our place input in 'suggest.html' as the place object
        document.getElementById('place').value = place;

        console.log(JSON.stringify(place));

        // Check place is in London
        const postalTown = getPostalTown(place);
        if (!postalTown) {
            // Show an error message
            alert("Error, please choose a different location in London.");
        } else if (postalTown !== "London") {
            // Show an error message
            alert("Location not found in London.");
        } else {
            // Run the rest of your code here
            console.log("The place is in London. Running the rest of the code...");
            // Your other code goes here
        

        // Display next section in form (and buttons)
        var step2 = document.getElementById('step2');
        var controls=document.getElementById('controls');

        // Remove the 'display: none;' style
        step2.style.display = '';
        controls.style.display = '';

        if (!place.geometry || !place.geometry.location) {
            // Invalid place or no location information available
            return;
        }

        // Set the map center to the selected place's location
        map.setCenter(place.geometry.location);
        map.setZoom(17); // Optionally, adjust the zoom level

        // Update the marker position and show it
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);

        // Fetch photos associated with the selected place
        var photos = place.photos;
        if (photos) {
            // Extract photo URLs
            var photoUrls = photos.map(function (photo) {
                return photo.getUrl({ maxWidth: 2500, maxHeight: 2500 }); // Adjust dimensions as needed
            });

            // Generate the image grid using the fetched photo URLs
            generateImageGrid(photoUrls);
        }

        // Get the img url from selected thumbnail
        var thumbnailElement = document.querySelector('.thumbnail.selected');
        var inputElement=document.getElementById('place_img_url')

        if (inputElement && thumbnailElement && thumbnailElement.querySelector('img')) {
            var imageUrl = thumbnailElement.querySelector('img').src;
            inputElement.value=imageUrl

        }


        // Autofill location info for next section
        var inputElement = document.getElementById('place_name');
        if (inputElement) {
            inputElement.value = place.name;
        }
        var inputElement = document.getElementById('place_location_address');
        if (inputElement) {
            inputElement.value = getTextBeforeLondonPostcode(place.formatted_address);
        }
        var inputElement = document.getElementById('place_location_postal_code');
        if (inputElement) {
            inputElement.value = getPostcodeFromPlace(place);
        }
        var inputElement = document.getElementById('place_google_place_gid');
        if (inputElement) {
            inputElement.value = place.place_id;
        }
        var inputElement = document.getElementById('place_location_lat');
        if (inputElement) {
            inputElement.value = place.geometry.location.lat();
        }
        var inputElement = document.getElementById('place_location_lng');
        if (inputElement) {
            inputElement.value = place.geometry.location.lng();
        }
        var inputElement = document.getElementById('place_borough');
        if (inputElement) {
            inputElement.value = getBoroughFromPlace(place);
        }
        var inputElement = document.getElementById('place_weekday_text');
        if (inputElement) {
            inputElement.value = place.opening_hours.weekday_text;
        }

        
        // Store the place name in the global variable
        globalPlaceName = place.name;}
        
    });

    // Function to handle thumbnail selection
    function selectThumbnail(thumbnailDiv, photoUrl) {
        // Remove 'selected' class from previously selected thumbnail (if any)
        var prevSelectedThumbnail = document.querySelector('.thumbnails.image_picker_selector .thumbnail.selected');
        if (prevSelectedThumbnail) {
            prevSelectedThumbnail.classList.remove('selected');
        }
        // Add 'selected' class to currently selected thumbnail
        thumbnailDiv.classList.add('selected');
        // Do something with the selected photo URL (e.g., display it, save it, etc.)
        console.log("Selected photo:", photoUrl);
    }

    function generateImageGrid(photoUrls) {
        var imageGrid = document.querySelector('.thumbnails.image_picker_selector');
        imageGrid.innerHTML = ''; // Clear existing content
    
        // Ensure we only display up to 6 images
        var maxImages = Math.min(photoUrls.length, 6);
    
        for (var i = 0; i < maxImages; i++) {
            // Create list item
            var listItem = document.createElement('li');
    
            // Create thumbnail div
            var thumbnailDiv = document.createElement('div');
            thumbnailDiv.className = 'thumbnail';
    
            // Create img element
            var img = document.createElement('img');
            img.className = 'image_picker_image';
            img.src = photoUrls[i];
    
            // Attach click event listener to select the thumbnail
            thumbnailDiv.addEventListener('click', (function(index) {
                return function() {
                    selectThumbnail(this, photoUrls[index]);
                };
            })(i));
    
            // Append img to thumbnail div
            thumbnailDiv.appendChild(img);
    
            // Append thumbnail div to list item
            listItem.appendChild(thumbnailDiv);
    
            // Append list item to image grid
            imageGrid.appendChild(listItem);
        }

        // Automatically select the first thumbnail
        var firstThumbnail = imageGrid.querySelector('.thumbnail');
        if (firstThumbnail) {
            selectThumbnail(firstThumbnail, photoUrls[0]);
        }
    
        // Show the image grid
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
