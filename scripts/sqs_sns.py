#!/usr/bin/env python
# SQS & SNS Script

import hashlib
import json
import logging
import sys
import threading
import time

import boto3
import daemon
import textblob

__author__ = 'He Li'
thread_num = 5
sqs_queue_url = 'https://sqs.us-west-2.amazonaws.com/523930296417/tweetmap'
sns_topic_arn = 'arn:aws:sns:us-west-2:523930296417:tweetmap'
logging.basicConfig(filename='sqs_sns.log', level=logging.INFO)


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
                QueueUrl=sqs_queue_url,
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
                    logging.info('Message(#{id}) has corrupted content... Skipped'.format(id=message[u'MessageId']))
                    continue
                # parse message
                parsed_message = json.loads(message[u'Body'])
                logging.info('Thread(#{thread_id}) fetch tweet(#{tweet_id})'.format(thread_id=self.id,
                                                                                    tweet_id=parsed_message[
                                                                                        u'tweet_id']))
                # determine and attach sentiment
                sentiment = textblob.TextBlob(parsed_message[u'text']).sentiment
                parsed_message['polarity'] = sentiment.polarity
                parsed_message['subjectivity'] = sentiment.subjectivity
                # pack message again
                packed_message = json.dumps(parsed_message)
                # publish to sns topic
                self.sns.publish(
                    TopicArn=sns_topic_arn,
                    Message=packed_message
                )
                response = self.sqs.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=message[u'ReceiptHandle']
                )


# daemon
class MyDaemon(daemon.Daemon):
    def __init__(self, pid_file):
        super(MyDaemon, self).__init__(pid_file)

    def run(self):
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


# main logic
if __name__ == "__main__":
    daemon = MyDaemon('/tmp/sqs_sns.pid')
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
