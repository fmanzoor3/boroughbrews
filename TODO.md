# TODO List

(branch: refactor/cafe-model)

-[x] Edit script.js so that if the location clicked on from google autocomplete is not within london then an error message pops up and the later stuff is not loaded

-[x] Rewrite how the address is formatted in script.js (maybe take formatted address and cut off at 'London')

-[x] Use jinja in our js script to perform a for loop over our cafe data (strings need to be within strings e.g. "{cafe.name}"; add something to settings.json to get rid of red underlines)

-[x] In the location page centre the map on the specific borough

-[x] Added a favicon.ico (the icon in the browser tab)

-[x] Pass place_id to show_cafe to properly obtain cafe_info

-[] Get more accurate coordinates for boroughs so they are centred better on the location page

-[x] Fix issue of buttons in under-review page [used :has(.highlight) in the css]

-[x] Finish the under-review form/page

-[] Create a file to store slugged names and their corresponding original names (as slug inverse doesnt seem to always be accurate)

-[] Link the criteria on the cafe page to the db
