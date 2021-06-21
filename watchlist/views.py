from flask import render_template, request, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user

from watchlist.models import User, Movie
from watchlist import app, db

# login page
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":

        users = User.query.all()
        if not users:
            flash("Please register first.")
            return redirect(url_for("index"))

        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Invalid input.")
            return redirect(url_for("login"))

        for user in users:
            if user.username == username and user.validate_password(password):
                login_user(user)
                flash("Login success.")
                return redirect(url_for("index"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))
    return render_template("login.html")

# log out
@app.route("/user/logout")
def logout():
    logout_user()
    flash("Goodbye.")
    return(redirect(url_for("index")))

# register
@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        users = User.query.all()
        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password or not name:
            flash("Invalid input.")
            return redirect(url_for("login"))

        for usr in users:
            if usr.username == username:
                flash("Username occupied, please choose a different username.")
                return redirect(url_for("register"))

        user = User(name = name, username = username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Account created.")
        return redirect(url_for("index"))

    return render_template("register.html")



# settings
@app.route("/user/settings", methods = ["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        name = request.form["name"]

        if not name or len(name) > 20:
            flash ("Invalid input.")
            return redirect(url_for("settings"))

        current_user.name = name
        db.session.commit()
        flash("Settings updated.")
        return redirect(url_for("index"))
    return render_template("settings.html")

# Movie list page & Manage input info
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('index'))
        movie = Movie(title = title, year = year, username = current_user.username)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    if current_user.is_authenticated:
        movies = Movie.query.filter_by(username = current_user.username).all()
    else:
        movies = Movie.query.all()
    return render_template('index.html', movies = movies)

# Editing page
@app.route("/movie/edit/<int:movie_id>", methods = ["GET", "POST"])
@login_required
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == "POST":
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) != 4 or len(title) > 60:
            flash("Invalid input.")
            return redirect(url_for("edit", movie_id = movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for('index'))

    return render_template('edit.html', movie = movie)

# Deleting records
@app.route("/movie/delete/<int:movie_id>", methods = ["GET", "POST"])
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash("Item deleted.")
    return redirect(url_for('index'))