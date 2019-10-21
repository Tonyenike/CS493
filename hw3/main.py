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
          "length": content["length"]})
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
        return 'Method not recogonized'

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

@app.route('/slips', methods=['POST','GET'])
def slips_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if not ("number" in content):
            return (json.dumps({"Error": "The request object is missing the required number"}), 400)
        new_slip = datastore.entity.Entity(key=client.key(constants.slips))
        new_slip.update({"number": content["number"], 
          "current_boat": None})
        client.put(new_slip)
        new_slip["id"] = new_slip.key.id
        new_slip["self"] = constants.link + constants.slips + "/" + str(new_slip.key.id)
        return json.dumps(new_slip), 201
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
            e["self"] = constants.link + constants.slips + "/" + str(e.key.id)
        return json.dumps(results)
    else:
        return 'Method not recogonized'

@app.route('/slips/<id>', methods=['GET', 'DELETE'])
def slips_delete(id):
    slip_key = client.key(constants.slips, int(id))
    slip = client.get(key=slip_key)
    if slip is None:
        return (json.dumps({"Error": "No slip with this slip_id exists"}), 404)
    if request.method == 'DELETE':
        client.delete(slip_key)
        return ('',204)
    elif request.method == 'GET':
        slip["id"]   = slip.key.id
        slip["self"] = constants.link + constants.slips + "/" + str(slip.key.id)
        return json.dumps(slip)
    else:
        return 'Method not recogonized'

@app.route('/slips/<slip_id>/<boat_id>', methods=['PUT', 'DELETE'])
def slips_put(slip_id, boat_id):
    slip_key = client.key(constants.slips, int(slip_id))
    boat_key = client.key(constants.boats, int(boat_id))
    slip = client.get(key=slip_key)
    boat = client.get(key=boat_key)
    if request.method == 'PUT':
        if (slip is None) or (boat is None):
            return (json.dumps({"Error": "The specified boat and/or slip don’t exist"}), 404)
        elif slip["current_boat"] is None:
            slip.update({"current_boat": boat_key.id})
            client.put(slip)
            return ('', 204)
        else:
            return (json.dumps({"Error": "The slip is not empty"}), 403)
    elif request.method == 'DELETE':
        if ((slip is None) or (boat is None)) or not (slip["current_boat"] == boat_key.id):
            return (json.dumps({"Error": "No boat with this boat_id is at the slip with this slip_id"}), 404)
        else:
            slip.update({"current_boat": None})
            client.put(slip)
            return ('', 204)
    else:
        return 'Method not recognized'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
