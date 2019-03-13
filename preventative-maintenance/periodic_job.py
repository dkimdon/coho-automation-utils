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

def load_rows():
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    SPREADSHEET_ID = '1EGhrt3WfEsQDmzMDjJz7jPEOxsAkEuZv-EChFjniZwk'
    RANGE_NAME = 'a1:z200'

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
    return result.get('values', [])


def select_tasks(today, rows):
    currentDay = today.day
    currentMonth = today.month
    currentYear = today.year

    indexes = {
        "subject": None,
        "email": None,
        "start": None,
        "interval": None,
        "month": None,
        "done": None,
        "body": None
    }
    # find the header row
    headerIdx=0
    for row in rows:
        for key in indexes:
            indexes[key] = None
        for idx in range(0, len(row)):
            for key, value in indexes.items():
                if key.lower() in row[idx].lower():
                    indexes[key] = idx
                    break
        headersFound = True
        for key in indexes:
            if indexes[key] == None:
                headersFound = False
        if headersFound:
            break
        else:
            headerIdx=headerIdx+1
        # If we found all values, break
    if not headersFound:
        return []

    tasks = []
    if not rows:
        print('No data found.')
    else:
        for row in rows[headerIdx+1:]:
            if len(row) < len(indexes):
              continue
            task = {}
            done = row[indexes['done']]
            if done != '':
                print('task is done, skipping')
                print(row)
                continue
            month = int(row[indexes['month']])
            if month != currentMonth:
                print('wrong month, skipping')
                continue
            task['email'] = row[indexes['email']]
            task['subject'] = row[indexes['subject']]
            task['body'] = row[indexes['body']]
            tasks.append(task)
    return tasks

def collect_tasks():
    rows = load_rows()
    print (rows)
    return #select_tasks(datetime.now(), rows)

if __name__ == '__main__':
    tasks = collect_tasks()
    for task in tasks:
        send_email(task['email'], task['subject'], task['body'])
        time.sleep(2)
