#!/bin/bash
set -e

export PATH=/home/ubuntu/coho-automation-utils/preventative-maintenance/venv/bin:$PATH

cd /home/ubuntu/coho-automation-utils/preventative-maintenance/

git pull
/home/ubuntu/coho-automation-utils/preventative-maintenance/periodic_job.py | logger -t preventative-maintenance
/home/ubuntu/coho-automation-utils/preventative-maintenance/periodic_job_gat.py | logger -t preventative-maintenance
