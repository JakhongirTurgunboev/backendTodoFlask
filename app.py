from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask, request, jsonify
from flask_apispec import FlaskApiSpec
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, marshal_with, fields
from flask_apispec.views import MethodResource
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

""" Configurations """

app = Flask(__name__)
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'G?h|*=]N8cpVnk='  # Change this to a strong secret key
jwt = JWTManager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

CORS(app)


app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Todo Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

taskFields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'task_text': fields.String,
    'status': fields.Boolean
 }


"""  Models  """


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return self.username


class Items(MethodResource, Resource):
    @marshal_with(taskFields)
    def get(self):
        tasks = Task.query.all()
        return tasks

    @marshal_with(taskFields)
    def post(self):
        data = request.json
        task = Task(username=data['username'], email=data['email'], task_text=data['task_text'], status=data['status'])
        db.session.add(task)
        db.session.commit()
        tasks = Task.query.all()
        return tasks


class Item(MethodResource, Resource):
    @marshal_with(taskFields)
    def get(self, pk):
        task = Task.query.filter_by(id=pk).first()
        return task

    @jwt_required()
    @marshal_with(taskFields)
    def put(self, pk):
        data = request.json
        task = Task.query.filter_by(id=pk).first()
        task.username = data['username']
        task.email = data['email']
        task.task_text = data['task_text']
        task.status = data['status']
        db.session.commit()
        return task

    @jwt_required()
    @marshal_with(taskFields)
    def delete(self, pk):
        task = Task.query.filter_by(id=pk).first()
        db.session.delete(task)
        db.session.commit()
        tasks = Task.query.all()
        return tasks


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    task_text = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.username


""" Routes and functions"""


@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify(message='Username already taken'), 400

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(message='User registered successfully'), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid username or password'), 401


api.add_resource(Items, '/api')
api.add_resource(Item, '/api/<int:pk>')


docs.register(Items)  # Register items endpoint
docs.register(Item)  # Register single item endpoint
docs.register(register)  # Register the registration endpoint
docs.register(login)  # Register the login endpoint


if __name__ == '__main__':
    app.run(debug=True)
