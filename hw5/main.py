from google.cloud import datastore
from flask import Flask, request
import json
import constants
from json2html import *
from cerberus import Validator

def isInt(value):
  try:
    int(value)
    return True
  except ValueError:
    return False

v = Validator()

v.schema = {
        "name": {
            "type": "string",
            "minlength": 1,
            "maxlength": 256,
            "regex": "[A-Za-z0-9 ]+",
            "required": True
        },
        "type": {
            "type": "string",
            "minlength": 1,
            "maxlength": 256,
            "regex": "[A-Za-z0-9 ]+",
            "required": True
        },
        "length": {
            "type": "integer",
            "min": 1, 
            "max": 10000,
            "required": True
        }
}

patchv = Validator()

patchv.schema = {
        "name": {
            "type": "string",
            "minlength": 1,
            "maxlength": 256,
            "regex": "[A-Za-z0-9 ]+",
        },
        "type": {
            "type": "string",
            "minlength": 1,
            "maxlength": 256,
            "regex": "[A-Za-z0-9 ]+",
        },
        "length": {
            "type": "integer",
            "min": 1, 
            "max": 10000,
        }
}

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

@app.route('/boats', methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        if not request.data:
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        content = request.get_json()
        if not v.validate(content):
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        q = client.query(kind=constants.boats)
        results = list(q.fetch())
        for e in results:
            if e["name"] == content["name"]:
                return (json.dumps({"Error": "Boat name already exists"}), 403, {"Content-Type": "application/json"})
        if (request.headers["Accept"]) and (not '*/*' in request.headers["Accept"]) and (not 'application/json' in request.headers["Accept"]):
            return (json.dumps({"Error": "Invalid accept header"}), 406, {"Content-Type": "application/json"})
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = constants.link + constants.boats + "/" + str(new_boat.key.id)
        return json.dumps(new_boat), 201, {"Content-Type": "application/json"}
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"]   = e.key.id
            e["self"] = constants.link + constants.boats + "/" + str(e.key.id)
        return json.dumps(results), 200, {"Content-Type": "application/json"}
    else:
        return json.dumps({"Error": "Method not recognized"}), 405, {"Content-Type": "application/json"}

@app.route('/boats/<id>', methods=['GET','PATCH','PUT','DELETE'])
def boats_put_delete(id):
    if (not isInt(id)):
        return (json.dumps({"Error": "No boat with this boat id exists"}), 404, {"Content-Type": "application/json"})
    boat_key = client.key(constants.boats, int(id))
    boat = client.get(key=boat_key)
    if boat is None:
        return (json.dumps({"Error": "No boat with this boat id exists"}), 404, {"Content-Type": "application/json"})
    if request.method == 'GET':
        if request.data:
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        if ("Accept" in request.headers):
            if ((not ('text/html' in request.headers["Accept"])) and 
                (not ('*/*' in request.headers["Accept"])) and 
                (not ('application/json' in request.headers["Accept"]))):
                return (json.dumps({"Error": "Invalid accept header"}), 406, {"Content-Type": "application/json"})
            elif ('application/json' in request.headers["Accept"]) or ('/*' in request.headers["Accept"]):
                boat["id"] = boat.key.id
                boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
                return json.dumps(boat), 200, {"Content-Type": "application/json"}
            else:
                boat["id"] = boat.key.id
                boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
                return json2html.convert(json = json.dumps(boat)), 200, {"Content-Type": "text/html"}
        boat["id"] = boat.key.id
        boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
        return json.dumps(boat), 200, {"Content-Type": "application/json"}
    elif request.method == 'PUT':
        if not request.data:
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        content = request.get_json()
        if not v.validate(content):
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        q = client.query(kind=constants.boats)
        results = list(q.fetch())
        for e in results:
            if (e["name"] == content["name"]) and (not e.key.id == boat.key.id):
                return (json.dumps({"Error": "Boat name already exists"}), 403, {"Content-Type": "application/json"})
        boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        client.put(boat)
        YEET = constants.link + constants.boats + "/" + str(boat.key.id)
        return ('', 303, {'Content-Type': 'application/json', 'Location': YEET})
    elif request.method == 'PATCH':
        # If there is no request data, the patch is still successful.
        # The boat just doesn't change.
        if not request.data:
            boat["id"] = boat.key.id
            boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
            return (json.dumps(boat), 200, {"Content-Type": "application/json"})
        content = request.get_json()
        if not patchv.validate(content):
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        if "name" in content:
            q = client.query(kind=constants.boats)
            results = list(q.fetch())
            for e in results:
                if (e["name"] == content["name"]) and (not e.key.id == boat.key.id):
                    return (json.dumps({"Error": "Boat name already exists"}), 403, {"Content-Type": "application/json"})
            boat.update({"name": content["name"]})
        if "type" in content:
            boat.update({"type": content["type"]})
        if "length" in content:
            boat.update({"length": content["length"]})
        if ("Accept" in request.headers) and (not ('*/*' in request.headers["Accept"])) and (not ('application/json' in request.headers["Accept"])):
            return (json.dumps({"Error": "Invalid accept header"}), 406, {"Content-Type": "application/json"})
        client.put(boat)
        boat["id"] = boat.key.id
        boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
        return(json.dumps(boat), 200, {"Content-Type": "application/json"})
    elif request.method == 'DELETE':
        if request.data:
            return (json.dumps({"Error": "The request object is invalid"}), 400, {"Content-Type": "application/json"})
        client.delete(boat_key)
        return ('',204, {"Content-Type": "application/json"})
    else:
        return json.dumps({"Error": "Method not recognized"}), 405, {"Content-Type": "application/json"}

@app.errorhandler(404)
def bigerror(e):
    return json.dumps({"Error": "Page does not exist"}), 404, {"Content-Type": "application/json"}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
