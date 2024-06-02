from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Enum, JSON
from geoalchemy2 import Geometry
import enum
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from datetime import date
import re
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap5(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class SeatRange(enum.Enum):
    RANGE_0_10 = "0-10"
    RANGE_10_20 = "10-20"
    RANGE_20_30 = "20-30"
    RANGE_30_40 = "30-40"
    RANGE_40_50 = "40-50"
    RANGE_50_PLUS = "50+"


class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=False)


# class Cafe(db.Model):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     place_id: Mapped[int] = mapped_column(String, unique=True, nullable=False)
#     name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
#     address: Mapped[str] = mapped_column(String(250), nullable=False)
#     img_url: Mapped[str] = mapped_column(String(250), nullable=False)
#     map_url: Mapped[str] = mapped_column(String(250), nullable=False)
#     location: Mapped[str] = mapped_column(String(250), nullable=False)
#     opening_hours: Mapped[str] = mapped_column(String, nullable=True)
#     wifi: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     sockets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     long_stay: Mapped[str] = mapped_column(
#         String(10), nullable=False, default="unknown"
#     )
#     tables: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     quiet: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     calls: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     vibe: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     groups: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     coffee: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     food: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     veggie: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     alcohol: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     credit_cards: Mapped[str] = mapped_column(
#         String(10), nullable=False, default="unknown"
#     )
#     light: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     outdoor: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     spacious: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     toilets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     access: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     ac: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     smoke_free: Mapped[str] = mapped_column(
#         String(10), nullable=False, default="unknown"
#     )
#     pets: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     parking: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
#     score: Mapped[str] = mapped_column(String(2), nullable=False, default="XX")


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
def make_slug(text):
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return slug


def make_slug_inverse(slug):
    return slug.replace("-", " ").title()


def check_cafe_in_db(address):
    print(address)
    # location= db.query.filter_by(address=address).first()


# ---------------------------------------------------ENV VARIABLES------------------------------------------------------------------------------------
google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")


# ------------------------------------------------------------------------------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {"google_api_key": google_api_key}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/all-locations")
def show_all_locations():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    locations = [cafe.location for cafe in cafes]
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
    cafes_at_location = db.session.query(Cafe).filter_by(location=location).all()
    cafe_names_slugged = [make_slug(cafe.name) for cafe in cafes_at_location]
    cafes = [
        {"cafe": cafes_at_location[i], "slugged_name": cafe_names_slugged[i]}
        for i in range(len(cafes_at_location))
    ]
    return render_template(
        "location.html", all_cafes=cafes, location_slug=location_slug
    )


@app.route("/<location_slug>/<cafe_slug>")
def show_cafe(location_slug, cafe_slug):
    location = make_slug_inverse(location_slug)
    cafe_name = make_slug_inverse(cafe_slug)
    print(cafe_name)
    cafe_info = (
        db.session.query(Cafe).filter_by(name=cafe_name, location=location).first()
    )
    print(cafe_info)
    return render_template("cafe.html", cafe=cafe_info)


# TODO: add_new_post() to create a new blog post
# @app.route("/new-post", methods=["GET", "POST"])
# def add_post():
#     create_post_form = CreatePostForm()
#     if create_post_form.validate_on_submit():
#         new_post = BlogPost(
#             title=create_post_form.title.data,
#             subtitle=create_post_form.subtitle.data,
#             date=date.today().strftime("%B %d, %Y"),
#             body=create_post_form.body.data,
#             author=create_post_form.author.data,
#             img_url=create_post_form.img_url.data,
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         return redirect(url_for("get_all_posts"))
#     return render_template("make-post.html", form=create_post_form)


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
    # if request.method == "POST":
    #     place_json = request.form.get("place[name]")
    #     print(place_json)
    #     new_cafe = Cafe(
    #         place_id=request.form.get("place[google_place_gid]"),
    #         name=request.form.get("place[name]"),
    #         address=request.form.get("place[location][address]"),
    #         img_url=request.form.get(),
    #         map_url=request.form.get(),
    #         location=request.form.get(),
    #         opening_hours=request.form.get(),
    #     )
    #     db.session.add(new_cafe)
    #     db.session.commit()
    return redirect(url_for("under_review", cafe_name="PLACEHOLDER"))


@app.route("/under-review/<cafe_name>")
def under_review(cafe_name):
    cafe = make_slug_inverse(cafe_name)
    return render_template("under-review.html", cafe_name=cafe)


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
