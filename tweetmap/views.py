# views for app & socket.io

from datetime import datetime

from flask import render_template, request, abort
from flask_socketio import emit
from tweetmap import app, io, es, sns

# import M2Crypto
import json
import requests

page_size = 50


@app.route('/')
def index():
    return render_template('index.html')


# Sample JSON request boy
# {
#   "Type" : "Notification",
#   "MessageId" : "da41e39f-ea4d-435a-b922-c6aae3915ebe",
#   "TopicArn" : "arn:aws:sns:us-west-2:123456789012:MyTopic",
#   "Subject" : "test",
#   "Message" : "test message",
#   "Timestamp" : "2012-04-25T21:49:25.719Z",
#   "SignatureVersion" : "1",
#   "Signature" : "EXAMPLElDMXvB8r9R83tGoNn0ecwd5UjllzsvSvbItzfaMpN2nk5HVSw7XnOn=",
#   "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService.pem",
#   "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe..."
# }
@app.route('/sns', methods=['POST'])
def sns_route():
    if u'x-amz-sns-message-type' not in request.headers:
        abort(400)
    message_type = request.headers[u'x-amz-sns-message-type']
    # get parsed sns_msg
    sns_msg = request.get_json(force=True)
    if sns_msg is None:
        abort(400)
    # validate signature
    if u'SignatureVersion' in sns_msg and sns_msg[u'SignatureVersion'] == '1':
        # TODO: validate message
        pass
    else:
        abort(400)

    if message_type == 'Notification':
        if u'Message' not in sns_msg:
            abort(400)
        # parse original message
        orig_msg = json.loads(sns_msg[u'Message'])
        cur_date = datetime.now()
        es.create(index='tweets-{y}.{m}.{d}'.format(y=cur_date.year, m=cur_date.month, d=cur_date.day),
                  doc_type='tweet', body=orig_msg)
    elif message_type == 'SubscriptionConfirmation':
        requests.get(sns_msg[u'SubscribeURL'])
        sns.confirm_subscription(
                TopicArn=sns_msg[u'TopicArn'],
                Token=sns_msg[u'Token']
        )
    elif message_type == 'UnsubscribeConfirmation':
        pass
    else:
        abort(400)
    return '', 204


# ops object
# {
#   page: Number
#   keywords: [String, String, ...]
# }
@io.on('search keywords')
def search_keywords(ops):
    # in case of None
    ops = {} if ops is None else ops
    page = 0 if u'page' not in ops else ops[u'page']
    keywords = [] if u'keywords' not in ops else ops[u'keywords']
    # page configuration
    item_begin = page * page_size
    # if it is not an array, make it an array
    if not isinstance(keywords, list):
        keywords = [keywords]
    # start search
    query_dsl = {
        'query': {
            'query_string': {
                'default_field': 'text',
                'query': ' OR '.join(keywords)
            }
        }
    }
    resp = es.search(index='', doc_type='', body=query_dsl, from_=item_begin, size=page_size)
    tweets = map(lambda t: t[u'_source'], resp[u'hits'][u'hits'])
    emit('keywords search', tweets)


# ops object
# {
#   coordinates: [[left_up_point][right_down_point]]
# }
@io.on('search geo')
def search_keywords(ops):
    if ops is None or u'coordinates' not in ops:
        emit('error', 'no coordinates specified')
    else:
        query_dsl = {
            'query': {
                'geo_shape': {
                    'location': {
                        'shape': {
                            'type': 'envelope',
                            'coordinates': ops[u'coordinates']
                        }
                    }
                }
            }
        }
        resp = es.search(index='', doc_type='', body=query_dsl, from_=0, size=300)
        tweets = map(lambda t: t[u'_source'], resp[u'hits'][u'hits'])
        emit('geo search', tweets)
