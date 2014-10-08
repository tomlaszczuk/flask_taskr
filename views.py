from flask import Flask, render_template, redirect, flash, session, url_for, \
    request, g
from functools import wraps
import sqlite3
from forms import AddTaskForm

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
            session['logged_in'] = True
            flash('Welcome %s' % request.form['username'])
            return redirect(url_for('tasks'))
    return render_template('login.html')


def fetch_task_data(data_set):
    return [dict(name=row[0], due_date=row[1], priority=row[2],
                 task_id=row[3]) for row in data_set]


@app.route('/tasks')
@login_required
def tasks():
    g.db = connect_db()
    cur = g.db.execute("""SELECT name, due_date, priority, task_id
        FROM tasks WHERE status=1;""")
    open_tasks = fetch_task_data(cur.fetchall())
    cur = g.db.execute("""SELECT name, due_date, priority, task_id
        FROM tasks WHERE status=0;""")
    closed_tasks = fetch_task_data(cur.fetchall())
    g.db.close()
    return render_template('tasks.html', form=AddTaskForm(request.form),
                           open_tasks=open_tasks, closed_tasks=closed_tasks)


@app.route("/add", methods=['POST'])
@login_required
def add_task():
    g.db = connect_db()
    name = request.form['name']
    priority = request.form['priority']
    date = request.form['due_date']
    if not name or not priority or not date:
        flash('All fields are required')
        g.db.close()
        return redirect(url_for('tasks'))
    else:
        g.db.execute("""INSERT INTO tasks (name, due_date, priority, status)
            VALUES (?, ?, ?, 1)""", [name, date, priority])
        g.db.commit()
        g.db.close()
        flash('New task has been successfully added')
        return redirect(url_for('tasks'))


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    g.db = connect_db()
    g.db.execute("""DELETE FROM tasks WHERE task_id="""+str(task_id))
    g.db.commit()
    g.db.close()
    flash('Task no.%d has been deleted' % task_id)
    return redirect(url_for('tasks'))


@app.route("/mark/<int:task_id>")
@login_required
def complete_task(task_id):
    g.db = connect_db()
    g.db.execute("""UPDATE tasks SET status=0 WHERE task_id="""+str(task_id))
    g.db.commit()
    g.db.close()
    flash("Task no.%d has been marked as completed" % task_id)
    return redirect(url_for('tasks'))
