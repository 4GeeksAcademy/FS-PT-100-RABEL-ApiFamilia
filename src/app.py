"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify(member), 200
    return jsonify({"error": "Member not found"}), 404

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    
    # Validación exhaustiva
    required = ["first_name", "age", "lucky_numbers"]
    if not all(field in data for field in required):
        raise APIException("Missing required fields", 400)
    
    if not isinstance(data["age"], int) or data["age"] <= 0:
        raise APIException("Invalid age", 400)
    
    if not isinstance(data["lucky_numbers"], list) or \
        not all(isinstance(n, int) for n in data["lucky_numbers"]):
        raise APIException("Invalid lucky numbers", 400)
    
    # Generar ID solo si no viene
    if "id" not in data:
        data["id"] = jackson_family._generate_id()
    elif not isinstance(data["id"], int):
        raise APIException("Invalid ID type", 400)
    
    jackson_family.add_member(data)
    return jsonify(data), 200

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    if jackson_family.delete_member(member_id):
        return jsonify({"done": True}), 200
    raise APIException("Member not found", 404)

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
