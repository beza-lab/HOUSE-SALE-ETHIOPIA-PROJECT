from flask import Flask, render_template, request, redirect, flash
from models import db, House, User
from werkzeug.utils import secure_filename
from models import User
import os

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user
)

app = Flask(__name__)


app.secret_key = "my-secret-key"

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///houses.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def home():

    houses = House.query.order_by(
        House.id.desc()
    ).limit(6).all()

    return render_template(
        "index.html",
        houses=houses
    )


@app.route("/add_house", methods=["GET", "POST"])
@login_required
def add_house():

    if request.method == "POST":


        image_file = request.files["image"]

        filename = secure_filename(
            image_file.filename
        )

        image_file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

        bedrooms = request.form.get("bedrooms", "0")
        bathrooms = request.form.get("bathrooms", "0")

        house = House(
            title=request.form["title"],
            price=float(request.form["price"]),
            city=request.form["city"],
            address=request.form["address"],
            bedrooms=int(bedrooms or 0),
            bathrooms=int(bathrooms or 0),
            description=request.form["description"],
            image=filename,
            owner_id=current_user.id
        )

        db.session.add(house)
        db.session.commit()

        return redirect("/listings")

    return render_template("add_house.html")


@app.route("/house/<int:id>")
def house_details(id):

    house = House.query.get_or_404(id)

    return render_template(
        "house_details.html",
        house=house
    )


@app.route("/listings")
def listings():

    houses = House.query.order_by(
        House.id.desc()
    ).all()

    return render_template(
        "listings.html",
        houses=houses
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and user.password == password:

            login_user(user)

            if user.role == "admin":
                return redirect("/admin")

            return redirect("/")

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return "Access Denied"

    houses = House.query.all()

    return render_template(
        "admin.html",
        houses=houses
    )


@app.route("/edit_house/<int:id>",
           methods=["GET", "POST"])
@login_required
def edit_house(id):

    house = House.query.get_or_404(id)

    if current_user.role != "admin" \
       and current_user.id != house.owner_id:

        return "Access Denied"

    if request.method == "POST":

        house.title = request.form["title"]
        house.price = float(request.form["price"])
        house.city = request.form["city"]
        house.address = request.form["address"]

        db.session.commit()

        return redirect("/listings")

    return render_template(
        "edit_house.html",
        house=house
    )

@app.route("/delete_house/<int:id>")
@login_required
def delete_house(id):

    house = House.query.get_or_404(id)

    if current_user.role == "admin" \
       or current_user.id == house.owner_id:

        db.session.delete(house)
        db.session.commit()

        return redirect("/listings")

    return "Access Denied"

@app.route("/house/<int:id>")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect("/register")

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            flash("Username already exists", "warning")

            return redirect("/register")


        if username == "admin":

            user = User(
                username=username,
                password=password,
                role="admin"
            )

        else:

            user = User(
                username=username,
                password=password,
                role="seller"
            )

        db.session.add(user)
        db.session.commit()

        
        flash("Registration successful. Please login.", "success")

        return redirect("/login")



    return render_template("register.html")

@app.route("/search")
def search():

    keyword = request.args.get("keyword", "")

    houses = House.query.filter(
        House.city.ilike(f"%{keyword}%") |
        House.title.ilike(f"%{keyword}%")
    ).all()

    return render_template(
        "listings.html",
        houses=houses
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)