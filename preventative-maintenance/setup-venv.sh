#!/bin/sh

python3 -m venv venv/
export PATH=`pwd`/venv/bin:$PATH

pip install boto3==1.16.47 botocore==1.19.47 certifi==2020.12.5 chardet==3.0.4 idna==2.10 jmespath==0.10.0 python-dateutil==2.9.0.post0 requests==2.24.0 s3transfer==0.3.7 six==1.17.0 urllib3==1.25.7
