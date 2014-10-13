import datetime
from functools import wraps
from flask import flash, request, redirect, session, url_for, render_template
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


@app.errorhandler(404)
def page_not_found(error):
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as log:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            log.write("\n404 error at %s: %s" % (current_timestamp, r))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as log:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            log.write("\n500 error at %s: %s" % (current_timestamp, r))
    return render_template('500.html'), 500
