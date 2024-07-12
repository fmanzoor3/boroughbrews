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

-[x] Report closed page

-[x] Add score and today's opening/closing time to cafes on location page

-[x] Make the corresponding cafe location popup in the map in the locations page when hovering over the cafe in the list

-[x] Make the search filter work on the location page

-[x] Order the list in the location page by score

-[x] Fix bug in cafe page when hovering over hearts

-[x] Store the images as image files so you dont have to rely on image urls that may change (i think the urls change after some time)

-[x] Make sure cafes with the same slugged name have distinct thumbnails

-[] Edit code so we download thumbnails only when the submit button is pressed (suggest page)

-[] Add a delete feature (later make it only accessible by admin)

-[x] Fix bugs associated with 'i-like-it' criteria button on location page

-[x] create front end of log-in, register and users pages

-[x] Complete back end of register page to put data in db

-[x] Set up relation database between users, cafes and reviews

-[x] Set up the log in system

-[x] Add photo path to User db

-[x] Implement reviews feature on cafe page

-[x] Add 'See more/less reviews' feature on cafe page and display correctly depending on if the user is logged in or not

-[x] Make popovers for the reviewers on cafe page

-[x] Add a user's visited cafes to users page

-[x] Take 'i_like_it' column of Cafe db and instead make a 'like_level' column in the user_cafe association table

-[x] Add a 'score' column in the user_cafe association table to have a different score for each user depending on their like_level of the cafe

-[x] Add 'Reported closed' column to Cafe

-[x] Redirect to log in page for places that require a logged in user (e.g. liking feature, leaving a review, rating criteria)

-[] Allow users to log in using Google

-[] Improve code by passing 'make_slug' function into templates when slug names are needed, instead of 'location_slug' and 'cafe_slugged'

-[] Create 'Remember me' and 'Forgot password' features on log in page

-[] Order reviews in order of most recent

-[x] Add 'edit' review feature

-[x] Change placeholder images

-[x] Change colour scheme

-[x] Check if uppercase text has become title case

-[x] Disable 'Liked' button in location page if not signed in

-[x] Fix bug that allows users to write more than one review per cafe

-[x] Add delete review feature for user's own comments (need to create a form so can POST)

-[x] Format Edit/Delete buttons in cafe page

-[x] Complete Top Rated Cafes section on home page

-[x] Format navbar to look nicer

-[x] Make the Restful routing/make endpoints sleeker

-[x] Check footer links

-[] Create contact email

-[] Check calculate score for bugs

-[x] Create requirements.txt

-[x] Host on WSGI server using gunicorn

-[x] Transfer SQLite dbs to PostgreSQL

-[x] Make padding-bottom larger for pages

-[x] Fix sign up link on home page

-[] Optimise home page image size

-[x] Locations page bug- can't press anything

-[x] Dropdown sometimes glitches and cant be pressed on mobile

-[] Map in suggest section too large on mobile

-[x] Redirect certain routes if user is authenticated etc
