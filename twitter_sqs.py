#!/usr/bin/env python
# Twitter Streaming Script

import json
import logging
import sys
import time

import boto3
import langdetect
import tweepy
from daemon import Daemon

__author__ = 'He Li'
sqs_queue_url = 'https://sqs.us-west-2.amazonaws.com/523930296417/tweetmap'
logging.basicConfig(filename='twitter_sqs.log', level=logging.INFO)


# custom listener
class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        super(MyStreamListener, self).__init__()
        # Queue connect
        self.queue = boto3.resource('sqs').get_queue_by_name(QueueName='tweetmap')

    def on_status(self, status):
        if status.coordinates is not None and status.coordinates[u'type'] == u'Point' and status.place is not None \
                and langdetect.detect(status.text) == 'en':
            # send message
            # noinspection PyBroadException
            try:
                self.queue.send_message(QueueUrl=sqs_queue_url,
                                        MessageBody=json.dumps({
                                            'tweet_id': status.id_str,
                                            'place_id': status.place.id,
                                            'user_id': status.user.id_str,
                                            'text': status.text,
                                            'username': status.user.screen_name,
                                            'user_profile_image': status.user.profile_image_url,
                                            'location': {
                                                'type': 'point',
                                                'coordinates': status.coordinates[u'coordinates']
                                            },
                                            'timestamp_ms': status.timestamp_ms
                                        }))
            except Exception as inst:
                logging.error(inst)
            else:
                # print message for debug
                logging.info('Tweet(#{id}) fetched'.format(id=status.id_str))

    def on_error(self, status_code):
        if status_code == 420:
            return False


# daemon
class MyDaemon(Daemon):
    def __init__(self, pid_file):
        super(MyDaemon, self).__init__(pid_file)
        # Twitter Auth
        auth = tweepy.OAuthHandler('piXrIVqsVCwtrAMZ24eC3VXBR', 'gU8uMs4TPErN0CvJogyU9mupoDvenxMaN7ZbeMHHvVpCTkb3LP')
        auth.set_access_token('699071431536152580-A5LQ0zP4D7s8AHVwECsNbne5uQVwvWa',
                              'E2x5miRE6gyyXTSWuYsTnPNcPrORcWP2F6RASWEHjRTdY')
        self.myStream = tweepy.Stream(auth=auth, listener=MyStreamListener())

    def run(self):
        while True:
            # start to fetch tweets
            logging.info('Twitter Fetch Script start now...')
            try:
                self.myStream.filter(track=['job', 'phone', 'love', 'china', 'the', 'a',
                                            'is', 'am', 'of', 'nyc', 'eat', 'friend', 'are'], async=False)
            except Exception as e:
                logging.error("error occurs: {err}, try to restart script".format(err=e))
            time.sleep(5)


# main logic
if __name__ == "__main__":
    daemon = MyDaemon('/tmp/twitter_sqs.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
