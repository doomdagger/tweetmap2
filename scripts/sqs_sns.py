# SQS & SNS Script

import boto3
import threading
import time
import hashlib
import textblob
import json

thread_num = 5


# Analyzer Class
class Analyzer(threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.sqs = boto3.client('sqs')
        self.sns = boto3.client('sns')

    def run(self):
        while True:
            response = self.sqs.receive_message(
                    QueueUrl='https://sqs.us-west-2.amazonaws.com/523930296417/tweetmap',
                    MaxNumberOfMessages=10,
                    VisibilityTimeout=15,
                    WaitTimeSeconds=10
            )
            # if empty response
            if u'Messages' not in response:
                time.sleep(3)
                continue
            # analyze tweets
            for message in response[u'Messages']:
                # validate md5
                if hashlib.md5(message[u'Body']).hexdigest() != message[u'MD5OfBody']:
                    print 'Message(#{id}) has corrupted content... Skipped'.format(id=message[u'MessageId'])
                    continue
                # parse message
                parsed_message = json.loads(message[u'Body'])
                print 'Thread(#{thread_id}) fetch tweet(#{tweet_id})'.format(thread_id=self.id,
                                                                             tweet_id=parsed_message[u'tweet_id'])
                # determine and attach sentiment
                sentiment = textblob.TextBlob(parsed_message[u'text']).sentiment
                parsed_message['polarity'] = sentiment.polarity
                parsed_message['subjectivity'] = sentiment.subjectivity
                # pack message again
                packed_message = json.dumps(parsed_message)
                # publish to sns topic
                self.sns.publish(
                        TopicArn='arn:aws:sns:us-west-2:523930296417:tweetmap',
                        Message=packed_message
                )
                response = self.sqs.delete_message(
                        QueueUrl='https://sqs.us-west-2.amazonaws.com/523930296417/tweetmap',
                        ReceiptHandle=message[u'ReceiptHandle']
                )


# initialize all threads
threads = [Analyzer(i) for i in range(thread_num)]
# start all threads
for thread in threads:
    thread.start()
    # start not in a rush
    time.sleep(0.5)
# join all threads
for thread in threads:
    thread.join()
