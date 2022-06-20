"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/todo', methods=['POST'])
def create_todo():
    body = request.get_json()
    todo = Todo(text=body["text"], done=False)
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.serialize())

@app.route('/todo', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    all_todos = list(map(lambda todo: todo.serialize(), todos))
    return jsonify(all_todos)

@app.route('/todo/<int:todo_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_todo(todo_id):
    if request.method == 'GET':
        todo = Todo.query.get(todo_id)
        if todo is None:
            raise APIException("Todo not found")
        return jsonify(todo.serialize())

    elif request.method == 'PUT':
        todo = Todo.query.get(todo_id)
        if todo is None:
            raise APIException("Todo not found")
        body = request.get_json()
        if not ('done' in body):
            raise APIException("no encontrado")
        todo.done = body['done']
        db.session.commit()
        return jsonify(todo.serialize())
        
    elif request.method == 'DELETE':
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return jsonify(todo.serialize())

    

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# this only runs if `$  ` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
