#!/usr/bin/env python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import time

def send_email(recipient, subject, body):
    AWS_REGION = "us-west-2"
    SENDER = "David Kimdon <dkimdon@gmail.com>"
    CHARSET = "UTF-8"

    client = boto3.client('ses',region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
                'CcAddresses': [
                    SENDER,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            ReplyToAddresses=[
                SENDER,
            ],
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

RECIPIENT = "dkimdon@gmail.com"
SUBJECT = "CoHo PM Task"
BODY_TEXT = ("Amazon SES Test (Python)\r\n"
             "This email was sent with Amazon SES using the "
             "AWS SDK for Python (Boto)."
            )

def collect_tasks():
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    SPREADSHEET_ID = '1EGhrt3WfEsQDmzMDjJz7jPEOxsAkEuZv-EChFjniZwk'
    RANGE_NAME = 'a3:z100'

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    currentMonth = datetime.now().month
    currentDay = datetime.now().day

    tasks = []
    if not values:
        print('No data found.')
    else:
        for row in values:
            task = {}
            column = 0
            done = row[column]
            if done != '':
                print('task is done, not sending mail')
                continue
            column += 1
            month = int(row[column])
            column += 1
            if month != datetime.now().month:
                print('wrong month, skipping')
                continue
            task['email'] = row[column]
            column += 1
            task['subject'] = row[column]
            column += 1
            task['body'] = row[column]
            column += 1
            tasks.append(task)
    return tasks

if __name__ == '__main__':
    tasks = collect_tasks()
    for task in tasks:
        send_email(task['email'], task['subject'], task['body'])
        time.sleep(2)
