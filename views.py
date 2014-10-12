import datetime
from functools import wraps
from flask import Flask, render_template, redirect, flash, session, url_for, \
    request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
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


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s"
                  % (getattr(form, field).label.text, error), 'error')


@app.route("/logout")
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('role', None)
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
                session['role'] = user.role
                flash("You have succesfully logged in, %s" % user.name)
                return redirect(url_for('tasks'))
        else:
            return render_template("login.html", form=form, error=error)
    return render_template("login.html", form=form)


@app.route('/tasks')
@login_required
def tasks():
    # checkin for errors (using get to avoid exceptions)
    name_errors = session.get('name_errors', None)
    due_date_errors = session.get('due_date_errors', None)
    session.pop('name_errors', None)
    session.pop('due_date_errors', None)

    user = User.query.get(session['user_id'])

    open_tasks = db.session.query(Task).filter_by(status='1').order_by(
        Task.due_date.asc())
    closed_tasks = db.session.query(Task).filter_by(status='0').order_by(
        Task.due_date.desc())
    return render_template('tasks.html', form=AddTaskForm(request.form),
                           open_tasks=open_tasks, closed_tasks=closed_tasks,
                           name_errors=name_errors,
                           due_date_errors=due_date_errors, user=user)


@app.route("/add", methods=['POST'])
@login_required
def add_task():
    form = AddTaskForm(request.form)
    if form.validate_on_submit():
        new_task = Task(name=form.name.data, due_date=form.due_date.data,
                        priority=form.priority.data,
                        posted_date=datetime.datetime.utcnow(),
                        status='1', user_id=session['user_id'])
        db.session.add(new_task)
        db.session.commit()
        flash("New task has been succesfully added")
    else:
        # we pass form errors to session dict
        # to display them on a page with different route
        session['name_errors'] = form.name.errors
        session['due_date_errors'] = form.due_date.errors
    return redirect(url_for('tasks'))


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('Task has been deleted')
    else:
        flash("You can only delete tasks that belong to you")
    return redirect(url_for('tasks'))


@app.route("/mark/<int:task_id>")
@login_required
def complete_task(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.update({'status': '0'})
        db.session.commit()
        flash("Task has been marked as completed")
    else:
        flash("You can only mark task that belong to you")
    return redirect(url_for('tasks'))


@app.route("/register", methods=["GET", "POST"])
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
                return redirect(url_for("login"))
            except IntegrityError:
                error = """That username and/or email address is
                already in use. Please try again."""
                return render_template("register.html", error=error, form=form)
        else:
            error = "Something gone wrong. Try again."
            return render_template("register.html", error=error, form=form)
    return render_template("register.html", form=form)
