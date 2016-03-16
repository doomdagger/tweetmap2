# views for app & socket.io

from tweetmap import app, io, es, sns_msg_source
from flask import render_template, request, abort
import json


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sns', methods=['POST'])
def sns():
    # validate msg source
    if u'x-amz-sns-topic-arn' not in request.headers or request.headers[u'x-amz-sns-topic-arn'] != sns_msg_source:
        abort(400)
    # get parsed sns_msg
    sns_msg = request.get_json()
    if u'Message' not in sns_msg:
        abort(400)
    # parse original message
    orig_msg = json.loads(sns_msg[u'Message'])
    es.create(index='test-index', doc_type='test-type', body=orig_msg)
