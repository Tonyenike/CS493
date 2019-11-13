from google.cloud import datastore
from flask import Flask, request
import json
import constants
from json2html import *
from cerberus import Validator
import logging
import random
import string
import requests

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


app = Flask(__name__)
client = datastore.Client()

mestring = randomString(10)
@app.route('/', methods=['GET'])
def index():
    mestring = randomString(10)
    return ("<a href='https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=200867782513-mekhm996b7tb3ngp1q1j249c8927m54u.apps.googleusercontent.com&redirect_uri=https://gobeavs2.appspot.com/oauth&scope=email profile&state=" + mestring + "'>Please follow this link to authorize.</a>")

@app.route('/oauth', methods=['GET'])
def specialty():
    if request.method == 'GET':
        params = {'client_id': '200867782513-mekhm996b7tb3ngp1q1j249c8927m54u.apps.googleusercontent.com',
                'grant_type' : 'authorization_code',
                'client_secret': 'egNn66zJWMM1xLBMjL8clj3v',
                'redirect_uri': 'https://gobeavs2.appspot.com/oauth',
                'code': request.args.get('code')}
        responsive = requests.post("https://www.googleapis.com/oauth2/v4/token", params=params, verify=False) 
        content = responsive.json()
        new_response = requests.get("https://people.googleapis.com/v1/people/me?personFields=names,emailAdresses",
                headers={'Authorization': ("Bearer " + content['access_token'])})
        new_content = new_response.json()
        return json.dumps(new_content)

@app.errorhandler(404)
def bigerror(e):
    return json.dumps({"Error": "Page does not exist"}), 404, {"Content-Type": "application/json"}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
