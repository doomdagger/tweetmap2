"""
    The __init__ file for package barter
"""
from flask import Flask
from flask_socketio import SocketIO
from elasticsearch import Elasticsearch
from boto3 import client
from certifi import where

__author__ = "He Li"

# make our app object
app = Flask(__name__)
io = SocketIO(app)
# config app
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
# connect es
es = Elasticsearch(hosts=['search-tweet2map-lldav6drz4p5byukwym7dplysa.us-west-2.es.amazonaws.com'],
                   port=443, use_ssl=True, verify_certs=True, ca_certs=where())
# sns
sns = client('sns')

import tweetmap.views
