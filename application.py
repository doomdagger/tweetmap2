#!/usr/bin/env python
# The main file, start our application here

from tweetmap import app, io
import logging

__author__ = "He Li"
logging.basicConfig(filename='tweetmap2.log', level=logging.DEBUG)
# add configuration for logger elasticsearch.tree
logger = logging.getLogger('elasticsearch.trace')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('tweetmap2.log')
fh.setLevel(logging.DEBUG)
# attach handler
logger.addHandler(fh)

if __name__ == '__main__':
    io.run(app, debug=True)
