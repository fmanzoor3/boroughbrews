from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    send_from_directory,
    flash,
)
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    String,
    Float,
    Boolean,
    Enum,
    JSON,
    Column,
    Text,
    ForeignKey,
    Table,
    cast,
)
import json
from dotenv import load_dotenv
import os
from static.utils.geo_utils import get_boroughs_data, find_borough
import re
from datetime import datetime
import math
import requests
from typing import List
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)
from werkzeug.security import generate_password_hash, check_password_hash

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

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Association table for the many-to-many relationship between users and cafes
user_cafe_association = Table(
    "user_cafe",
    db.Model.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("cafe_id", Integer, ForeignKey("cafes.id"), primary_key=True),
    Column("like_level", String, default="unknown"),
    Column("score", String, default="XX"),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    surname: Mapped[str] = mapped_column(String(250), nullable=False)
    occupation: Mapped[str] = mapped_column(String(250), default="Friendly Co-Worker")
    privacy: Mapped[str] = mapped_column(String(250), default="0")
    photo_name: Mapped[str] = mapped_column(String(250), default="anonymous.png")
    visited_cafes: Mapped[List["Cafe"]] = relationship(
        "Cafe", secondary=user_cafe_association, back_populates="visitors"
    )
    reviews: Mapped[List["Review"]] = relationship(back_populates="author")

    def get_like_level(self, cafe_id):
        association = (
            db.session.query(user_cafe_association)
            .filter_by(user_id=self.id, cafe_id=cafe_id)
            .first()
        )
        return association.like_level if association else "unknown"

    def get_score(self, cafe_id):
        association = (
            db.session.query(user_cafe_association)
            .filter_by(user_id=self.id, cafe_id=cafe_id)
            .first()
        )
        cafe = db.get_or_404(Cafe, cafe_id)
        return association.score if association else cafe.score

    def get_review_for_cafe(self, cafe_id):
        review = (
            db.session.query(Review)
            .filter_by(author_id=self.id, cafe_id=cafe_id)
            .first()
        )
        return review


class Cafe(db.Model):
    __tablename__ = "cafes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    place_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(250), nullable=False)
    borough: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    map_url: Mapped[str] = mapped_column(String(250), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    opening_hours = Column(JSON, default={})
    criterion = Column(JSON, default={})
    score: Mapped[str] = mapped_column(String(2), nullable=False, default="XX")
    visitors: Mapped[List["User"]] = relationship(
        "User", secondary=user_cafe_association, back_populates="visited_cafes"
    )
    reviews: Mapped[List["Review"]] = relationship(back_populates="parent_cafe")
    reported_closed: Mapped[str] = mapped_column(
        String(250), nullable=False, default="False"
    )


class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    author: Mapped["User"] = relationship(back_populates="reviews")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    parent_cafe: Mapped["Cafe"] = relationship(back_populates="reviews")
    cafe_id: Mapped[int] = mapped_column(Integer, ForeignKey("cafes.id"))


with app.app_context():
    db.create_all()


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


def check_cafe_in_db(place_id):
    cafe = db.session.query(Cafe).filter_by(place_id=place_id).first()
    if cafe:
        print(cafe.id)
        return {
            "exists": True,
            "id": cafe.id,
            "location_slug": make_slug(cafe.borough),
            "cafe_slug": make_slug(cafe.name),
        }
    return {"exists": False}


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


def calculate_score(criterion, like_level):
    if any(value == "unknown" for key, value in criterion.items()):
        return "XX"
    score = 0

    base_scores = {
        "wifi": 11,
        "sockets": 11,
        "long_stay": 5.5,
        "tables": 5.5,
        "quiet": 3,
        "calls": 3,
    }
    default_base_score = 11 / 15

    for key, value in criterion.items():
        base_score = base_scores.get(key, default_base_score)

        if value == "medium":
            score += base_score
        elif value == "high":
            score += base_score * 2

    score = round(score)

    if like_level == "low":
        score = ((score - 0.1) // 10) * 10
    elif like_level == "medium":
        score = ((score - 0.1) // 10) * 10 + 5
    elif like_level == "high":
        score = math.ceil(score / 10) * 10
    return str(int(score))


def download_image(url, save_path="image.jpg"):
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as file:
            file.write(response.content)
        return "Image successfully downloaded: " + save_path
    else:
        return "Failed to retrieve the image"


def get_like_level(self, cafe_id):
    association = (
        db.session.query(user_cafe_association)
        .filter_by(user_id=self.id, cafe_id=cafe_id)
        .first()
    )
    return association.like_level


def user_has_review_filter(reviews, user_id):
    return any(review.author.id == user_id for review in reviews)


def obtain_top_cafes():
    top_cafes = (
        db.session.query(Cafe).order_by(cast(Cafe.score, Integer).desc()).limit(3).all()
    )
    return top_cafes


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
    top_cafes = obtain_top_cafes()
    return render_template("index.html", top_cafes=top_cafes, make_slug=make_slug)


# Borough pages
@app.route("/boroughs")
def show_all_locations():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    locations = [cafe.borough for cafe in cafes]
    all_unique_locations = list(set(locations))  # set removes duplicates from our list
    all_unique_locations.sort()  # sort alphabetically
    return render_template(
        "all-locations.html", borough_names=all_unique_locations, make_slug=make_slug
    )


@app.route("/boroughs/<location_slug>")
def show_location(location_slug):
    location = make_slug_inverse(location_slug)
    lat = borough_coords[location]["lat"]
    lng = borough_coords[location]["lng"]
    cafes_at_location = (
        db.session.query(Cafe)
        .filter_by(borough=location, reported_closed="False")
        .all()
    )

    current_day = datetime.now().strftime("%a")
    return render_template(
        "location.html",
        all_cafes=cafes_at_location,
        borough_lat=lat,
        borough_lng=lng,
        current_day=current_day,
        make_slug=make_slug,
    )


# Cafe pages
@app.route("/cafes/<cafe_id>", methods=["GET", "POST"])
def show_cafe(cafe_id):
    edit_review = request.args.get("edit_review", "false")
    cafe_info = db.get_or_404(Cafe, cafe_id)
    current_day = datetime.now().strftime("%a")
    return render_template(
        "cafe.html",
        cafe=cafe_info,
        current_day=current_day,
        edit_review=edit_review,
        user_has_review_filter=user_has_review_filter,
        make_slug=make_slug,
    )


@app.route("/cafes/<cafe_id>/submitting-review", methods=["POST"])
def submit_review(cafe_id):
    cafe_info = db.get_or_404(Cafe, cafe_id)
    current_date = datetime.now().strftime("%B %d, %Y")

    existing_review = (
        db.session.query(Review)
        .filter_by(author_id=current_user.id, cafe_id=cafe_info.id)
        .first()
    )

    if existing_review:
        existing_review.text = request.form.get("review[desc]")
        existing_review.date = str(current_date)
    else:
        new_review = Review(
            text=request.form.get("review[desc]"),
            author=current_user,
            date=str(current_date),
            parent_cafe=cafe_info,
        )
        db.session.add(new_review)

    association = (
        db.session.query(user_cafe_association)
        .filter_by(user_id=current_user.id, cafe_id=cafe_info.id)
        .first()
    )

    if not association:
        stmt = user_cafe_association.insert().values(
            user_id=current_user.id,
            cafe_id=cafe_info.id,
            like_level="unknown",
            score=cafe_info.score,
        )
        db.session.execute(stmt)

    db.session.commit()
    return redirect(url_for("show_cafe", cafe_id=cafe_info.id))


@app.route("/cafes/<cafe_id>/deleting-review")
def delete_review(cafe_id):
    cafe_info = db.get_or_404(Cafe, cafe_id)

    # Retrieve the existing review
    existing_review = (
        db.session.query(Review)
        .filter_by(author_id=current_user.id, cafe_id=cafe_info.id)
        .first()
    )

    if existing_review:
        db.session.delete(existing_review)

        # Optionally, you can remove the association if needed
        association = (
            db.session.query(user_cafe_association)
            .filter_by(user_id=current_user.id, cafe_id=cafe_info.id)
            .first()
        )

        if association:
            db.session.execute(
                user_cafe_association.delete().where(
                    (user_cafe_association.c.user_id == current_user.id)
                    & (user_cafe_association.c.cafe_id == cafe_info.id)
                )
            )

        db.session.commit()

    return redirect(url_for("show_cafe", cafe_id=cafe_id))


@app.route("/cafes/<cafe_id>/report-closed")
def report_closed(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    cafe.reported_closed = "True"
    db.session.commit()
    return redirect(url_for("show_location", location_slug=make_slug(cafe.borough)))


@app.route("/cafes/<cafe_id>/<like_score>")
def i_like_it(cafe_id, like_score):
    cafe = db.get_or_404(Cafe, cafe_id)
    criterion = dict(cafe.criterion)
    score = calculate_score(criterion, like_score)

    # Check if the association exists
    association = (
        db.session.query(user_cafe_association)
        .filter_by(user_id=current_user.id, cafe_id=cafe.id)
        .first()
    )

    if association:
        # Update the like_level if the association exists
        db.session.query(user_cafe_association).filter_by(
            user_id=current_user.id, cafe_id=cafe.id
        ).update({"like_level": like_score, "score": score})
    else:
        # Add the cafe to the user's visited cafes with the like_level if the association does not exist
        stmt = user_cafe_association.insert().values(
            user_id=current_user.id, cafe_id=cafe.id, like_level=like_score, score=score
        )
        db.session.execute(stmt)

    db.session.commit()
    return redirect(url_for("show_cafe", cafe_id=cafe_id))


@app.route("/cafes/<cafe_id>/edit", methods=["GET", "POST"])
def edit(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    cafe_name = make_slug(cafe.name)
    if request.method == "POST":
        like_level = request.form.get("criterion[i_like_it]")
        cafe.criterion = {
            "wifi": request.form.get("criterion[wifi]"),
            "sockets": request.form.get("criterion[sockets]"),
            "long_stay": request.form.get("criterion[long_stay]"),
            "tables": request.form.get("criterion[tables]"),
            "quiet": request.form.get("criterion[quiet]"),
            "calls": request.form.get("criterion[calls]"),
            "vibe": request.form.get("criterion[vibe]"),
            "groups": request.form.get("criterion[groups]"),
            "coffee": request.form.get("criterion[coffee]"),
            "food": request.form.get("criterion[food]"),
            "veggie": request.form.get("criterion[veggie]"),
            "alcohol": request.form.get("criterion[alcohol]"),
            "credit_cards": request.form.get("criterion[credit_cards]"),
            "light": request.form.get("criterion[light]"),
            "outdoor": request.form.get("criterion[outdoor]"),
            "spacious": request.form.get("criterion[spacious]"),
            "toilets": request.form.get("criterion[toilets]"),
            "access": request.form.get("criterion[access]"),
            "ac": request.form.get("criterion[ac]"),
            "pets": request.form.get("criterion[pets]"),
            "parking": request.form.get("criterion[parking]"),
        }
        cafe.score = calculate_score(cafe.criterion, "unknown")
        db.session.commit()
        return redirect(
            url_for(
                "show_cafe",
                cafe_id=cafe.id,
            )
        )
    return render_template("under-review.html", cafe=cafe)


# Suggest and under-review pages
@app.route("/suggest")
def suggest():
    return render_template("suggest.html")


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
            opening_hours=format_opening_hours(request.form.get("place[weekday_text]")),
        )
        db.session.add(new_cafe)
        db.session.commit()
        new_cafe_id = new_cafe.id
        create_slug(place_name)
        create_slug(borough)
    return redirect(url_for("under_review", cafe_id=new_cafe_id))


@app.route("/under-review//cafes/<cafe_id>", methods=["GET", "POST"])
def under_review(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    if request.method == "POST":
        like_level = request.form.get("criterion[i_like_it]")
        cafe.criterion = {
            "wifi": request.form.get("criterion[wifi]"),
            "sockets": request.form.get("criterion[sockets]"),
            "long_stay": request.form.get("criterion[long_stay]"),
            "tables": request.form.get("criterion[tables]"),
            "quiet": request.form.get("criterion[quiet]"),
            "calls": request.form.get("criterion[calls]"),
            "vibe": request.form.get("criterion[vibe]"),
            "groups": request.form.get("criterion[groups]"),
            "coffee": request.form.get("criterion[coffee]"),
            "food": request.form.get("criterion[food]"),
            "veggie": request.form.get("criterion[veggie]"),
            "alcohol": request.form.get("criterion[alcohol]"),
            "credit_cards": request.form.get("criterion[credit_cards]"),
            "light": request.form.get("criterion[light]"),
            "outdoor": request.form.get("criterion[outdoor]"),
            "spacious": request.form.get("criterion[spacious]"),
            "toilets": request.form.get("criterion[toilets]"),
            "access": request.form.get("criterion[access]"),
            "ac": request.form.get("criterion[ac]"),
            "pets": request.form.get("criterion[pets]"),
            "parking": request.form.get("criterion[parking]"),
        }
        cafe.score = calculate_score(cafe.criterion, "unknown")
        db.session.commit()
        return redirect(
            url_for(
                "show_cafe",
                cafe_id=cafe.id,
            )
        )
    return render_template("under-review.html", cafe=cafe)


## Authentication pages
@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        id = current_user.id
        user = db.get_or_404(User, id)
        user.name = request.form.get("user[name]")
        user.surname = request.form.get("user[surname]")
        user.occupation = request.form.get("user[occupation]")
        if request.form.get("user[anonymous]"):
            user.privacy = request.form.get("user[anonymous]")
        else:
            user.privacy = "0"
        profile_pic = request.files["user[avatar]"]
        if profile_pic:
            filename = profile_pic.filename
            file_path = os.path.join("static/assets/images/profile-pics", filename)
            profile_pic.save(file_path)
            user.photo_name = filename
        db.session.commit()
        return redirect(url_for("users"))
    return render_template("users.html", make_slug=make_slug)


@app.route("/users/login", methods=["GET", "POST"])
def log_in():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    if request.method == "POST":
        user = db.session.execute(
            db.select(User).where(User.email == request.form.get("user[email]"))
        ).scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("log_in"))
        elif (
            check_password_hash(user.password, request.form.get("user[password]"))
            == False
        ):
            flash("Password incorrect, please try again.")
            return redirect(url_for("log_in"))
        else:
            login_user(user)
            return redirect(url_for("users"))
    return render_template("log-in.html")


@app.route("/users/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users"))
    if request.method == "POST":
        user = db.session.execute(
            db.select(User).where(User.email == request.form.get("user[email]"))
        ).scalar()
        if user:
            flash("You've already signed up with this email, log in instead!")
            return redirect(url_for("log_in"))
        elif len(request.form.get("user[password]")) < 8:
            flash("Password is too short (minimum is 8 characters).")
            return redirect(url_for("register"))
        elif request.form.get("user[password]") != request.form.get(
            "user[password_confirmation]"
        ):
            flash("Password confirmation doesn't match Password, please try again.")
            return redirect(url_for("register"))
        else:
            new_user = User(
                email=request.form.get("user[email]"),
                password=generate_password_hash(
                    request.form.get("user[password]"),
                    method="pbkdf2:sha256",
                    salt_length=8,
                ),
                name=request.form.get("user[name]"),
                surname=request.form.get("user[surname]"),
            )

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("users"))
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


## Other routes
# Downloading cafe thumbnails
@app.route("/download_image", methods=["POST"])
def download_image_endpoint():
    data = request.json
    url = data.get("url")
    image_name = re.sub(r"[^a-z0-9-]", "", data.get("name").lower().replace(" ", "-"))
    save_path = os.path.join(
        "static", "assets", "images", "thumbnails", f'{data.get("id")}-{image_name}.jpg'
    )
    result = download_image(url, save_path)
    return jsonify({"message": result, "path": save_path})


@app.route("/api/check_cafe")
def check_cafe():
    place_id = request.args.get("place_id")
    result = check_cafe_in_db(place_id)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
