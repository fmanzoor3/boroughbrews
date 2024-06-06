from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    send_from_directory,
)
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, Boolean, Enum, JSON
from geoalchemy2 import Geometry
import enum
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import json
from dotenv import load_dotenv
import os
from static.utils.geo_utils import get_boroughs_data, find_borough
import re
from datetime import datetime

# from static.utils.format_open_hours import format_opening_hours, day_abbreviations

# Load environment variables from .env file
load_dotenv()

# Obtain London boroughs geo_data
boroughs_data = get_boroughs_data()
with open("data/borough_coordinates.json", "r") as json_file:
    borough_coords = json.load(json_file)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[int] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(250), nullable=False)
    borough: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    map_url: Mapped[str] = mapped_column(String(250), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    opening_hours: Mapped[str] = mapped_column(String, nullable=True)
    wifi: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    sockets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    long_stay: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown"
    )
    tables: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    quiet: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    calls: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    vibe: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    groups: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    coffee: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    food: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    veggie: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    alcohol: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    credit_cards: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown"
    )
    light: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    outdoor: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    spacious: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    toilets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    access: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    ac: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    smoke_free: Mapped[str] = mapped_column(
        String(10), nullable=False, default="unknown"
    )
    pets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    parking: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    score: Mapped[str] = mapped_column(String(2), nullable=False, default="XX")


with app.app_context():
    db.create_all()


# # CREATE FORM
# class CreatePostForm(FlaskForm):
#     title = StringField("Blog Post Title", validators=[DataRequired()])
#     subtitle = StringField("Subtitle", validators=[DataRequired()])
#     author = StringField("Your name", validators=[DataRequired()])
#     img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
#     body = CKEditorField("Blog Content", validators=[DataRequired()])
#     submit = SubmitField("Done")


# -------------------------------------------FUNCTIONS---------------------------------------------------------------------------
# Here we create a function to convert words into url format e.g. convert the string London Bridge to london-bridge
def create_slug(text):
    file_path = "data/slugged_names.json"

    try:
        with open(file_path, "r") as file:
            content = file.read()
            if content.strip():
                data = json.loads(content)
            else:
                data = {}
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        data = {}

    slug = re.sub(r"[^a-z0-9-]", "", text.lower().replace(" ", "-"))

    if text not in data:
        data[text] = slug

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Slug for '{text}' added successfully: {slug}")
    else:
        print(f"Slug for '{text}' already exists: {data[text]}")


def make_slug(text):
    with open("data/slugged_names.json", "r") as file:
        data = json.load(file)
    return data[text]


def make_slug_inverse(slug):
    with open("data/slugged_names.json", "r") as file:
        data = json.load(file)
    for key, val in data.items():
        if val == slug:
            return key


def check_cafe_in_db(address):
    print(address)
    # location= db.query.filter_by(address=address).first()


def format_opening_hours(weekday_text):
    day_abbreviations = {
        "Monday": "Mon",
        "Tuesday": "Tue",
        "Wednesday": "Wed",
        "Thursday": "Thu",
        "Friday": "Fri",
        "Saturday": "Sat",
        "Sunday": "Sun",
    }
    try:
        weekday_text = (
            weekday_text.replace(" ", " ")
            .replace("–", "-")
            .replace("\u202f", " ")
            .replace("\u2009", " ")
        )
        first_split = re.split(",(?=\w)", weekday_text)
        opening_hours_dict = {}

        for i in first_split:
            weekday, time_range = i.split(":", 1)
            weekday = weekday.strip()
            time_range = time_range.strip()

            if time_range.lower() == "closed":
                opening_hours_dict[day_abbreviations[weekday]] = "Closed"
                continue
            elif time_range.lower() == "open 24 hours":
                opening_hours_dict[day_abbreviations[weekday]] = "Open 24 hours"
                continue
            elif "hours might differ" in time_range.lower():
                opening_hours_dict[day_abbreviations[weekday]] = time_range
                continue

            time_range = re.sub(r"\s*\(.*?\)", "", time_range.strip())
            start_time, end_time = time_range.split("-")
            try:
                formatted_start_time = datetime.strptime(
                    start_time.strip(), "%I:%M %p"
                ).strftime("%H:%M")
            except ValueError:
                formatted_start_time = datetime.strptime(
                    start_time.strip(), "%H:%M"
                ).strftime("%H:%M")
            try:
                formatted_end_time = datetime.strptime(
                    end_time.strip(), "%I:%M %p"
                ).strftime("%H:%M")
            except ValueError:
                formatted_end_time = datetime.strptime(
                    end_time.strip(), "%H:%M"
                ).strftime("%H:%M")
            opening_hours_dict[day_abbreviations[weekday]] = (
                f"{formatted_start_time} – {formatted_end_time}"
            )
        return opening_hours_dict
    except Exception as e:
        print(f"Error processing {i}: {e}")
        return {
            "Mon": "N/A",
            "Tue": "N/A",
            "Wed": "N/A",
            "Thu": "N/A",
            "Fri": "N/A",
            "Sat": "N/A",
            "Sun": "N/A",
        }


# ---------------------------------------------------ENV VARIABLES------------------------------------------------------------------------------------
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")


# ------------------------------------------------------------------------------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {"google_api_key": google_api_key}


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all-locations")
def show_all_locations():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    locations = [cafe.borough for cafe in cafes]
    all_unique_locations = list(set(locations))  # set removes duplicates from our list
    all_unique_locations.sort()  # sort alphabetically
    location_names_slugged = [make_slug(location) for location in all_unique_locations]
    locations = [
        {"name": all_unique_locations[i], "slugged-name": location_names_slugged[i]}
        for i in range(len(all_unique_locations))
    ]
    return render_template("all-locations.html", all_locations=locations)


@app.route("/<location_slug>")
def show_location(location_slug):
    location = make_slug_inverse(location_slug)
    lat = borough_coords[location]["lat"]
    lng = borough_coords[location]["lng"]
    cafes_at_location = db.session.query(Cafe).filter_by(borough=location).all()
    cafe_names_slugged = [make_slug(cafe.name) for cafe in cafes_at_location]
    cafes = [
        {"cafe": cafes_at_location[i], "slugged_name": cafe_names_slugged[i]}
        for i in range(len(cafes_at_location))
    ]
    return render_template(
        "location.html",
        all_cafes=cafes,
        location_slug=location_slug,
        borough_lat=lat,
        borough_lng=lng,
    )


@app.route("/<location_slug>/<cafe_slug>")
def show_cafe(location_slug, cafe_slug):
    id = request.args.get("id")
    cafe_info = db.get_or_404(Cafe, id)
    return render_template(
        "cafe.html",
        cafe=cafe_info,
        location_slug=location_slug,
        cafe_slug=cafe_slug,
        id=cafe_info.id,
    )


@app.route("/suggest", methods=["GET", "POST"])
def suggest(coordinates=[]):
    if request.method == "POST":
        place_json = request.form.get("place")
        print(place_json)
        # json_data = json.loads(place_json)
        # print(json_data["name"])
        # print(f"{selected_location},{latitude},{longitude}")
        # if longitude and latitude:
        #     coordinates = [latitude, longitude]
        #     print(coordinates)
        # check_cafe_in_db(location_address)
    return render_template("suggest.html", coordinates=coordinates)


@app.route("/suggests", methods=["GET", "POST"])
def suggests():
    if request.method == "POST":
        place_id = request.form.get("place[google_place_gid]")
        place_name = request.form.get("place[name]")
        lat = request.form.get("place[location][lat]")
        lng = request.form.get("place[location][lng]")
        borough = find_borough(lat, lng, boroughs_data)

        new_cafe = Cafe(
            place_id=place_id,
            name=place_name,
            address=request.form.get("place[location][address]"),
            postal_code=request.form.get("place[location][postal_code]"),
            borough=borough,
            img_url=request.form.get("place[img_url]"),
            map_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
            lat=lat,
            lng=lng,
            opening_hours=json.dumps(
                format_opening_hours(request.form.get("place[weekday_text]"))
            ),
        )
        db.session.add(new_cafe)
        db.session.commit()
        new_cafe_id = new_cafe.id
        create_slug(place_name)
        create_slug(borough)
    return redirect(
        url_for("under_review", cafe_name_slugged=make_slug(place_name), id=new_cafe_id)
    )


@app.route("/under-review/<cafe_name_slugged>/<id>", methods=["GET", "POST"])
def under_review(cafe_name_slugged, id):
    cafe_name = make_slug_inverse(cafe_name_slugged)
    if request.method == "POST":
        id = request.form.get("id")
        cafe = db.get_or_404(Cafe, id)
        cafe.wifi = request.form.get("criterion[wifi]")
        location_slug = make_slug(cafe.borough)
        cafe_slug = make_slug(cafe.name)
        db.session.commit()
        return redirect(
            url_for(
                "show_cafe",
                location_slug=location_slug,
                cafe_slug=cafe_slug,
                id=id,
            )
        )
    return render_template(
        "under-review.html", cafe_name_slugged=cafe_name_slugged, id=id
    )


@app.route("/<location_slug>/<cafe_name_slugged>/edit", methods=["GET", "POST"])
def edit(cafe_name_slugged, location_slug):
    cafe_name = make_slug_inverse(cafe_name_slugged)
    id = request.args.get("id")
    if request.method == "POST":
        id = request.form.get("id")
        cafe = db.get_or_404(Cafe, id)
        cafe.wifi = request.form.get("criterion[wifi]")
        location_slug = make_slug(cafe.borough)
        cafe_slug = make_slug(cafe.name)
        db.session.commit()
        return redirect(
            url_for(
                "show_cafe",
                location_slug=location_slug,
                cafe_slug=cafe_slug,
                id=id,
            )
        )
    return render_template(
        "under-review.html", cafe_name_slugged=cafe_name_slugged, id=id
    )


# TODO: edit_post() to change an existing blog post
# @app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
# def edit_post(post_id):
#     post = db.get_or_404(BlogPost, post_id)
#     edit_form = CreatePostForm(
#         title=post.title,
#         subtitle=post.subtitle,
#         img_url=post.img_url,
#         author=post.author,
#         body=post.body,
#     )
#     if edit_form.validate_on_submit():
#         post.title = edit_form.title.data
#         post.subtitle = edit_form.subtitle.data
#         post.img_url = edit_form.img_url.data
#         post.author = edit_form.author.data
#         post.body = edit_form.body.data
#         db.session.commit()
#         return redirect(url_for("show_post", post_id=post.id))
#     return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: delete_post() to remove a blog post from the database
# @app.route("/delete/<post_id>")
# def delete_post(post_id):
#     post = db.get_or_404(BlogPost, post_id)
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for("get_all_posts"))


# # Below is the code from previous lessons. No changes needed.
# @app.route("/about")
# def about():
#     return render_template("about.html")


# @app.route("/contact")
# def contact():
#     return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
