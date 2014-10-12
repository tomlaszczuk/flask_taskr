import datetime
from flask import render_template, redirect, flash, session, url_for, \
    request, Blueprint
from project import db
from project.models import Task, User
from project.views import login_required
from .forms import AddTaskForm

tasks_blueprint = Blueprint('tasks', __name__, url_prefix="/tasks",
                            template_folder='templates',
                            static_folder="static")


@tasks_blueprint.route('/')
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


@tasks_blueprint.route("/add", methods=['POST'])
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
    return redirect(url_for('tasks.tasks'))


@tasks_blueprint.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.delete()
        db.session.commit()
        flash('Task has been deleted')
    else:
        flash("You can only delete tasks that belong to you")
    return redirect(url_for('tasks.tasks'))


@tasks_blueprint.route("/mark/<int:task_id>")
@login_required
def complete_task(task_id):
    task = db.session.query(Task).filter_by(task_id=task_id)
    if session['user_id'] == task.first().user_id or session['role'] == "admin":
        task.update({'status': '0'})
        db.session.commit()
        flash("Task has been marked as completed")
    else:
        flash("You can only mark task that belong to you")
    return redirect(url_for('tasks.tasks'))
