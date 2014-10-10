import datetime
from functools import wraps
from flask import Flask, render_template, redirect, flash, session, url_for, \
    request
from flask.ext.sqlalchemy import SQLAlchemy
from forms import AddTaskForm, RegisterForm, LoginForm

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
from models import Task, User


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap


@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash("You are now logged out. Thank you, come again")
    return redirect(url_for('login'))


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
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
                flash("You have succesfully logged in")
                return redirect(url_for('tasks'))
        else:
            return render_template("login.html", form=form, error=error)
    return render_template("login.html", form=form)


@app.route('/tasks')
@login_required
def tasks():
    open_tasks = db.session.query(Task).filter_by(status='1').order_by(
        Task.due_date.asc())
    closed_tasks = db.session.query(Task).filter_by(status='0').order_by(
        Task.due_date.desc())
    return render_template('tasks.html', form=AddTaskForm(request.form),
                           open_tasks=open_tasks, closed_tasks=closed_tasks)


@app.route("/add", methods=['POST'])
@login_required
def add_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(name=form.name.data, due_date=form.due_date.data,
                            priority=form.priority.data,
                            posted_date=datetime.datetime.utcnow(),
                            status='1', user_id=session['user_id'])
            db.session.add(new_task)
            db.session.commit()
            flash("New task has been succesfully added")
    return redirect(url_for('tasks'))


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    db.session.query(Task).filter_by(task_id=task_id).delete()
    db.session.commit()
    flash('Task has been deleted')
    return redirect(url_for('tasks'))


@app.route("/mark/<int:task_id>")
@login_required
def complete_task(task_id):
    db.session.query(Task).filter_by(task_id=task_id).update({"status": "0"})
    db.session.commit()
    flash("Task has been marked as completed")
    return redirect(url_for('tasks'))


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            new_user = User(name=form.name.data, email=form.email.data,
                            password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("You have been succesfully registered. Please login.")
            return redirect(url_for("login"))
        else:
            error = "Something gone wrong. Try again."
            return render_template("register.html", error=error, form=form)
    return render_template("register.html", form=form)
