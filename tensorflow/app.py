"""
from flask import Flask, jsonify,make_response, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import numpy
import tensorflow as tf
import requests
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]

def UserExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True

def verify_pw(username, password):
    hashed_pw = users.find({"Username": username})[0]["Password"]
    if bcrypt.hashpw(password.encode("utf8"), hashed_pw)== hashed_pw:
        return True
    else:
        return False

def generateReturnDictionary(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return retJson

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Username doesn't exist please register first"), True

    correct_pw = verify_pw(username, password)
    if not correct_pw:
        return generateReturnDictionary(302, "Password is Incorrect"), True

    return None, False

class Register(Resource):
    def post(self):

        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        if UserExist(username):
            retJson={
                "status": 301,
                "msg": "This username is allready registered"
            }
            return jsonify(retJson)



        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg" : "Registered successfully"
        }
        return jsonify(retJson)

class Classify(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]
        url = postedData["url"]

        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)

        tokens = users.find({
            "Username": username
        })[0]["Tokens"]

        if tokens <= 0:
            return jsonify(generateReturnDictionary(303, "Not Enough Tokens"))

        r = requests.get(url)
        retJson = {}
        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                retJson = json.load(g)

        users.update({
            "Username" : username
        },{
            "$set": {"Tokens" : tokens-1}
        })
        return retJson

class Refill(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["admin_pw"]
        amount = postedData["amount"]

        if not UserExist(username):
            return jsonify(generateReturnDictionary(301, "Username doesn't exist"))

        correct_pw = "abc123"

        if not password == correct_pw:
            return jsonify(generateReturnDictionary(301, "Incorrect password"))

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": amount
            }
        })

        return jsonify(generateReturnDictionary(200, "Refilled successfully"))

api.add_resource(Register, "/register")
api.add_resource(Classify, "/classify")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(host = "0.0.0.0")

"""


from flask import Flask, jsonify, make_response, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
import bcrypt
from pymongo import MongoClient
import numpy
import requests
import tensorflow as tf
import subprocess
import json
from werkzeug import secure_filename
import os

app = Flask(__name__)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]
# let's define the root path

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

def UserExist(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True

def verify_pw(username, password):
    hashed_pw = users.find({"Username": username})[0]["Password"]
    if bcrypt.hashpw(password.encode("utf8"), hashed_pw)== hashed_pw:
        return True
    else:
        return False

def generateReturnDictionary(status, msg):
    retJson = {
        "status": status,
        "msg": msg
    }
    return retJson

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Username doesn't exist please register first"), True

    correct_pw = verify_pw(username, password)
    if not correct_pw:
        return generateReturnDictionary(302, "Password is Incorrect"), True

    return None, False

@app.route("/register", methods =["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())

        if UserExist(username):
            retJson={
                "status": 301,
                "msg": "This username is allready registered"
            }
            return jsonify(retJson)

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Tokens": 6
        })

        retJson = {
            "status": 200,
            "msg" : "Registered successfully"
        }
        return jsonify(retJson)
    return render_template("register.html")


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'send' in request.form:
            target = os.path.join(APP_ROOT, 'images/')
            print(target)

            if not os.path.isdir(target):
                os.mkdir(target)

            for file in request.files.getlist("file"):
                # this will return the list of filename
                print(file)
                filename = file.filename
                # we need to tell the server that store this file to specific location
                destination = "/".join([target, filename])
                print(destination)
                file.save(destination)

                proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file={}'.format(destination), shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.communicate()[0]
                proc.wait()
                with open("text.txt") as g:
                    retJson = json.load(g)
            return jsonify(retJson)

        elif 'link' in request.form:
            url = request.form["url"]
            r = requests.get(url)
            with open("temp.jpg", "wb") as f:
                f.write(r.content)
                proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.communicate()[0]
                proc.wait()
                with open("text.txt") as g:
                    retJson = json.load(g)
            return jsonify(retJson)
    return render_template("complete.html")

@app.route("/refill", methods = ["GET", "POST"])
def refill():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["admin_pw"]
        amount = request.form["amount"]

        if not UserExist(username):
            return jsonify(generateReturnDictionary(301, "Username doesn't exist"))

        correct_pw = "abc123"

        if not password == correct_pw:
            return jsonify(generateReturnDictionary(301, "Incorrect password"))

        users.update({
            "Username": username
        }, {
            "$set": {
                "Tokens": amount
            }
        })

        return jsonify(generateReturnDictionary(200, "Refilled successfully"))
    return render_template("Refill.html")


if __name__ == "__main__":
    app.run(debug = True, host= "0.0.0.0")
