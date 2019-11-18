from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import numpy
import requests
import tensorflow as tf
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]


class Classify(Resource):
    def post(self):
        postedData = request.get_json()
        url = postedData["url"]
        r = requests.get(url)
        print("hello"+ url)
        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                retJson = json.load(g)

        return retJson

api.add_resource(Classify, "/classify")

if __name__ == "__main__":
    app.run(host = "0.0.0.0")


# this is perfect working code
"""

url = "http://blogs.discovermagazine.com/d-brief/files/2019/02/Zebra.jpg"
r = requests.get(url)
print("hello"+ url)
with open("temp.jpg", 'wb') as f:
    f.write(r.content)
    proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.communicate()[0]
    proc.wait()
    with open("text.txt") as g:
        retJson = json.load(g)

print(retJson)
"""


"""
# working code

from flask import Flask, jsonify,make_response, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
from pymongo import MongoClient
import numpy
import requests
import tensorflow as tf
import subprocess
import json

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]

@app.route("/classify", methods=["GET", "POST"])
def Classify():
    if request.method == "POST":
        #GET form fields
        url = request.form["url"]
        r = requests.get(url)
        print("hello"+ url)
        with open("temp.jpg", "wb") as f:
            f.write(r.content)
            proc = subprocess.Popen('python3 classify_image.py --model_dir=. --image_file=./temp.jpg', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()[0]
            proc.wait()
            with open("text.txt") as g:
                retJson = json.load(g)

        return retJson
    return render_template("clasification.html")

if __name__ == "__main__":
    app.run(debug = True, host= "0.0.0.0")

"""

"""
# It's 100 per working
# for checking tensorflow installation
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import numpy
import requests
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.ImageRecognition
users = db["Users"]

class Classify(Resource):
    def post(self):
        hello = tf.constant('Hello, TensorFlow! furqan')
        sess = tf.compat.v1.Session()
        print(sess.run(hello))
        return "Hello this is runnig"

api.add_resource(Classify, "/classify")

if __name__ == "__main__":
    app.run(host = "0.0.0.0")
"""

"""
# this is working API with both docker and flask

from flask import Flask, jsonify, make_response, request, render_template, redirect, url_for, session, logging
from flask_restful import Api, Resource
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

@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():
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
    return render_template("complete.html")

"""
