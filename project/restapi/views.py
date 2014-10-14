from flask import Blueprint, request, jsonify, make_response
from project import db
from project.models import Task

restapi_blueprint = Blueprint('restapi', __name__, url_prefix='/api')


@restapi_blueprint.route('/tasks', methods=['GET'])
def tasks():
    if request.method == 'GET':
        results = db.session.query(Task).limit(10).offset(0).all()
        json_results = []
        for result in results:
            data = {
                'task_id': result.task_id,
                'task_name': result.name,
                'due date': str(result.due_date),
                'priority': result.priority,
                'posted_date': str(result.posted_date),
                'status': str(result.status),
                'user_id': result.user_id
            }
            json_results.append(data)
    return jsonify(items=json_results)


@restapi_blueprint.route('/task/<int:task_id>', methods=['GET'])
def task(task_id):
    if request.method == 'GET':
        results = db.session.query(Task).get(task_id)
        if results:
            json_results = {
                'task_id': results.task_id,
                'task_name': results.name,
                'due date': str(results.due_date),
                'priority': results.priority,
                'posted_date': str(results.posted_date),
                'status': str(results.status),
                'user_id': results.user_id
            }
            return jsonify(items=json_results)
        else:
            results = {"sorry": "There is nothing here"}
            code = 404
            return make_response(jsonify(results), code)
