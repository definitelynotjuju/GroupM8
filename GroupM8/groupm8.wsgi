#!/usr/bin/python
import sys

#Configuration with WSGI

#Enables error logging for Apache
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/GroupM8/")

#Importing the Flask App
from GroupM8 import app as application
application.secret_key = 'Add your secret key'
