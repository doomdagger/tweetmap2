#!/usr/bin/env python
# The main file, start our application here

import logging

from tweetmap import app, io

__author__ = "He Li"
logging.basicConfig(filename='tweetmap2.log', level=logging.DEBUG)

if __name__ == '__main__':
    io.run(app, host='0.0.0.0', port=5000, debug=True)
