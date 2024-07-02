# TODO List

-[x] Edit script.js so that if the location clicked on from google autocomplete is not within london then an error message pops up and the later stuff is not loaded

-[x] Rewrite how the address is formatted in script.js (maybe take formatted address and cut off at 'London')

-[x] Use jinja in our js script to perform a for loop over our cafe data (strings need to be within strings e.g. "{cafe.name}"; add something to settings.json to get rid of red underlines)

-[x] In the location page centre the map on the specific borough

-[x] Added a favicon.ico (the icon in the browser tab)

-[x] Pass place_id to show_cafe to properly obtain cafe_info

-[] Get more accurate coordinates for boroughs so they are centred better on the location page

-[x] Fix issue of buttons in under-review page [used :has(.highlight) in the css]

-[x] Finish the under-review form/page

-[x] Create a file to store slugged names and their corresponding original names (as slug inverse doesnt seem to always be accurate)

-[x] Link the criteria on the cafe page to the db; go through the page and put in the required data-content, progress-bar and span values

-[x] Use datetime to format opening hours and store this as a json in the db

-[x] Create a function to catch when a cafe is already in the db

-[x] Turn the criterion in the db into one JSON

-[x] Autofill the cafe-edit page with the current criteria data

-[x] Make the current day bold in the opening hours in the cafe page

-[x] Make the 'i_like_it' functionality work on the cafe page [KEY: when updating a JSON column need to make sure it is a dict]

-[x] Use a formula to calculate the cafe score [See txt file for break down]

-[] Report closed page

-[x] Add score and today's opening/closing time to cafes on location page

-[x] Make the corresponding cafe location popup in the map in the locations page when hovering over the cafe in the list

-[x] Make the search filter work on the location page

-[x] Order the list in the location page by score

-[x] Fix bug in cafe page when hovering over hearts

-[x] Store the images as image files so you dont have to rely on image urls that may change (i think the urls change after some time)

-[x] Make sure cafes with the same slugged name have distinct thumbnails

-[] Edit code so we download thumbnails only when the submit button is pressed (suggest page)

-[] Make the API restful

-[] Add a delete feature (later make it only accessible by admin)

-[x] Fix bugs associated with 'i-like-it' criteria button on location page

-[] Change placeholder images

-[] Change colour scheme

-[x] create front end of log-in, register and users pages

-[x] Complete back end of register page to put data in db

-[x] Set up relation database between users, cafes and reviews

-[x] Set up the log in system

-[x] Add photo path to User db

-[x] Implement reviews feature on cafe page

-[] Add 'See more/less reviews' feature on cafe page

-[] Make popovers for the reviewers on cafe page

-[] Allow users to log in using Google
