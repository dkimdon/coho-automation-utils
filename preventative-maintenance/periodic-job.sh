#!/bin/sh

export PATH=/home/ubuntu/coho-automation-utils/preventative-maintenance/venv/bin:$PATH

git pull
/home/ubuntu/coho-automation-utils/preventative-maintenance/periodic-job.py
