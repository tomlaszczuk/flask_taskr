from functools import wraps
from flask import flash, redirect, session, url_for
from project import app, db


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('users.login'))
    return wrap


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s"
                  % (getattr(form, field).label.text, error), 'error')


@app.route('/', defaults={'page': 'index'})
def index(page):
    return redirect(url_for('tasks.tasks'))
