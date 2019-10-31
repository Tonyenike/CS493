from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

@app.route('/boats', methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if not (("name" in content) and ("type" in content) and ("length" in content)):
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], "type": content["type"],
            "length": content["length"], "loads": []})
        client.put(new_boat)
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = constants.link + constants.boats + "/" + str(new_boat.key.id)
        return json.dumps(new_boat), 201
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"]   = e.key.id
            e["self"] = constants.link + constants.boats + "/" + str(e.key.id)
        return json.dumps(results)
    else:
        return json.dumps({"Error": "Method not recognized"}), 400

@app.route('/boats/<id>', methods=['GET','PATCH','DELETE'])
def boats_put_delete(id):
    boat_key = client.key(constants.boats, int(id))
    boat = client.get(key=boat_key)
    if boat is None:
        return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
    if request.method == 'GET':
        boat["id"] = boat.key.id
        boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
        return json.dumps(boat)
    elif request.method == 'PATCH':
        content = request.get_json()
        if not (("name" in content) and ("type" in content) and ("length" in content)):
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
        boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"]})
        client.put(boat)
        boat["id"] = boat.key.id
        boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
        return (json.dumps(boat),200)
    elif request.method == 'DELETE':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            if e["current_boat"] == boat_key.id:
                e["current_boat"] = None
                client.put(e)
        client.delete(boat_key)
        return ('',204)
    else:
        return json.dumps({"Error": "Method not recognized"}), 400


@app.route('/loads', methods=['POST','GET'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if not (("content" in content) and ("weight" in content)):
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({"content": content["content"], "weight": content["weight"], "carrier": None})
        client.put(new_load)
        new_load["id"] = new_load.key.id
        new_load["self"] = constants.link + constants.loads + "/" + str(new_load.key.id)
        return json.dumps(new_load), 201
    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        results = list(query.fetch())
        for e in results:
            if not(e["carrier"] is None):
                boat_key = client.key(constants.boats, int(e["carrier"]))
                boat = client.get(key=boat_key)
                if boat is None:
                    return (json.dumps({"Error": "No boat with this boat_id exists"}), 404)
                boat["id"] = boat.key.id
                boat["self"] = constants.link + constants.boats + "/" + str(boat.key.id)
                e["carrier"] = boat 
            e["id"]   = e.key.id
            e["self"] = constants.link + constants.loads + "/" + str(e.key.id)
        return json.dumps(results)
    else:
        return json.dumps({"Error": "Method not recognized"}), 400

@app.route('/loads/<id>', methods=['GET','PATCH','DELETE'])
def loads_put_delete(id):
    load_key = client.key(constants.loads, int(id))
    load = client.get(key=load_key)
    if load is None:
        return (json.dumps({"Error": "No load with this load_id exists"}), 404)
    if request.method == 'GET':
        load["id"] = load.key.id
        load["self"] = constants.link + constants.loads + "/" + str(load.key.id)
        return json.dumps(load)
    elif request.method == 'PATCH':
        content = request.get_json()
        if not (("content" in content) and ("weight" in content)):
            return (json.dumps({"Error": "The request object is missing at least one of the required attributes"}), 400)
        client.put(load)
        load["id"] = load.key.id
        load["self"] = constants.link + constants.loads + "/" + str(load.key.id)
        return (json.dumps(load),200)
    elif request.method == 'DELETE':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            if load_key.id is in e["current_load"]:
                e["current_load"] = None
                client.put(e)
        client.delete(load_key)
        return ('',204)
    else:
        return json.dumps({"Error": "Method not recognized"}), 400

@app.route('/loads/<boat_id>/<load_id>', methods=['PUT', 'DELETE'])
def move_load_boat(boat_id, load_id):


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
