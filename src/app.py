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
from models import db, User, Characters, Planets, Favorites
import json
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
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

########################
#       Usuarios       #
########################

# Muestra todos los usuarios
@app.route('/user', methods=['GET'])
def get_all_users():
    user = User.query.all()
    if user == []: 
        return jsonify({"msg": "No existe ningún usuario"}), 404
    results = list(map(lambda x: x.serialize(), user))
    return jsonify(results), 200

# Busca por id de usuario
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    userId = User.query.filter_by(id=user_id).first()
    if userId is None: 
        return jsonify({"msg": "No existe el usuario"}), 404
    return jsonify(userId.serialize()), 200

# Alta de un usuario
@app.route('/user', methods=['POST'])
def addUser():
    body = json.loads(request.data)

    queryNewUser = User.query.filter_by(email=body["email"]).first()
    
    if queryNewUser is None:
        new_user = User(
            username=body["username"], 
            email=body["email"], 
            password=body["password"]
        )
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify(new_user.serialize()), 201
    return jsonify({"msg": "Usuario ya creado"}), 404

# Borra un usuario
@app.route('/user/<int:user_id>', methods=['DELETE'])
def deleteUser(user_id):
    userId = User.query.filter_by(id=user_id).first()
  
    if userId is None: 
        return jsonify({"msg": "Usuario no encontrado"}), 404

    db.session.delete(userId)
    db.session.commit()
    return jsonify({"msg": "Usuario borrado"}), 204

# Modifica un usuario por id
@app.route('/user/<int:user_id>', methods=['PUT'])
def usersModif_porId(user_id):
    usuario = User.query.filter_by(id=user_id).first()
    body = json.loads(request.data)

    if usuario is None:
        return jsonify({"msg": "No existe el usuario"}), 400    

    if "email" in body:
        usuario.email = body["email"]
    if "password" in body:
        usuario.password = body["password"]
    if "username" in body:
        usuario.username = body["username"]
    
    db.session.commit()
    return jsonify({"msg": "Usuario modificado"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
