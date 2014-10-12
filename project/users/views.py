from flask import render_template, redirect, flash, session, url_for, \
    request, Blueprint
from sqlalchemy.exc import IntegrityError
from project import db
from project.views import login_required
from project.models import User
from .forms import RegisterForm, LoginForm

users_blueprint = Blueprint('users', __name__, url_prefix='/users',
                            template_folder='templates',
                            static_folder='static')


@users_blueprint.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash("You are now logged out. Thank you, come again")
    return redirect(url_for('users.login'))


@users_blueprint.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(
                name=request.form['name'], password=request.form['password']
            ).first()
            if user is None:
                error = "Invalid username or password"
                return render_template("login.html", form=form, error=error)
            else:
                session['logged_in'] = True
                session['user_id'] = user.id
                session['role'] = user.role
                flash("You have succesfully logged in, %s" % user.name)
                return redirect(url_for('tasks.tasks'))
        else:
            return render_template("login.html", form=form, error=error)
    return render_template("login.html", form=form)


@users_blueprint.route("/register", methods=["GET", "POST"])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            new_user = User(name=form.name.data, email=form.email.data,
                            password=form.password.data)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("You have been succesfully registered. Please login.")
                return redirect(url_for("users.login"))
            except IntegrityError:
                error = """That username and/or email address is
                already in use. Please try again."""
                return render_template("register.html", error=error, form=form)
        else:
            error = "Something gone wrong. Try again."
            return render_template("register.html", error=error, form=form)
    return render_template("register.html", form=form)
