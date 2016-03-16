# Twitter Streaming Script

import tweepy
import boto3
import langdetect
import json

__author__ = 'He Li'


# custom listener
class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        super(MyStreamListener, self).__init__()
        # Queue connect
        self.queue = boto3.resource('sqs').get_queue_by_name(QueueName='tweetmap')

    def on_status(self, status):
        if status.coordinates is not None and status.coordinates[u'type'] == u'Point' and langdetect.detect(
                status.text) == 'en':
            # send message
            # noinspection PyBroadException
            try:
                self.queue.send_message(QueueUrl='https://sqs.us-west-2.amazonaws.com/523930296417/tweetmap',
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
                print inst
            else:
                # print message for debug
                print status.text

    def on_error(self, status_code):
        if status_code == 420:
            return False


# Twitter Auth
auth = tweepy.OAuthHandler('piXrIVqsVCwtrAMZ24eC3VXBR', 'gU8uMs4TPErN0CvJogyU9mupoDvenxMaN7ZbeMHHvVpCTkb3LP')
auth.set_access_token('699071431536152580-A5LQ0zP4D7s8AHVwECsNbne5uQVwvWa',
                      'E2x5miRE6gyyXTSWuYsTnPNcPrORcWP2F6RASWEHjRTdY')

myStream = tweepy.Stream(auth=auth, listener=MyStreamListener())
# start to fetch tweets
myStream.filter(track=['job'], async=False)
