#!/bin/sh

python3 -m venv venv/
export PATH=`pwd`/venv/bin:$PATH

pip install google-api-python-client oauth2client boto3

