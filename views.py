from functools import wraps
from flask import Flask, render_template, redirect, flash, session, url_for, \
    request
from flask.ext.sqlalchemy import SQLAlchemy
from forms import AddTaskForm

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
from models import Task


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
    flash("You are now logged out. Thank you, come again")
    return redirect(url_for('login'))


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] \
                or request.form['password'] != app.config['PASSWORD']:
            flash('Invalid username or password. Please try again')
        else:
            session['logged_in'] = True
            flash('Welcome %s' % request.form['username'])
            return redirect(url_for('tasks'))
    return render_template('login.html')


@app.route('/tasks')
@login_required
def tasks():
    open_tasks = db.session.query(Task).filter_by(status='1').order_by(
        Task.due_date.asc())
    closed_tasks = db.session.query(Task).filter_by(status='0').order_by(
        Task.due_date.asc())
    return render_template('tasks.html', form=AddTaskForm(request.form),
                           open_tasks=open_tasks, closed_tasks=closed_tasks)


@app.route("/add", methods=['POST'])
@login_required
def add_task():
    form = AddTaskForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_task = Task(name=form.name.data, due_date=form.due_date.data,
                            priority=form.priority.data, status='1')
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
