from flask import Flask, render_template, redirect, flash, session, url_for, \
    request
from functools import wraps
import sqlite3

app = Flask(__name__)
app.config.from_object('config')


def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])


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
            flash('Welcome %s' % request.form['username'])
            return redirect(url_for('tasks'))
    return render_template('login.html')
