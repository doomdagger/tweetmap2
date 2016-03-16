#!/usr/bin/env python
# The main file, start our application here

from tweetmap import app
import logging

__author__ = "He Li"
logging.basicConfig(filename='tweetmap2.log', level=logging.INFO)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
