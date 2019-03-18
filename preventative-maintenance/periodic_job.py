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

    intro="""Hello,
    Thank you for being the owner of this CoHo preventative maintenance task as you are contributing to the longevity of our physical community. As the owner of the task we are asking you to do the following:
    - Do the task in the month scheduled or let Denis White capeblanco@peak.org know when you will complete the task or if you are unable to do so.
    - When task is completed send an email back to Denis when the task was completed with the  information that should be recorded in the PM task history.
    - If the task is unclear or you need additional informational to safely complete the task please ask Bruce or Denis.\n
    - If the task is to be competed on a work party day you are responsible for notifying the work day coordinator and coordinating or getting assistance for your task.\n"""

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
                        'Data': intro + body,
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
    currentMonth = today.strftime("%B").lower()[0:3]
    currentYear = today.year

    indexes = {
        "subject": None,
        "email": None,
        "year interval": None,
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

    todo = []
    if not rows:
        print('No data found.')
    else:
        for row in rows[headerIdx+1:]:
            if len(row) < len(indexes):
              continue
            task = {}
            done = row[indexes['done']]
            (monthDone, yearDone) = done.split(",")

            yearInterval = int(row[indexes['year interval']])

            if currentYear < int(yearDone) + yearInterval:
                continue
            
            month = row[indexes['month']].lower()[0:3]
            if month != currentMonth:
                continue
            task['email'] = row[indexes['email']]
            task['subject'] = row[indexes['subject']]
            task['body'] = row[indexes['body']]
            todo.append(task)

    return { 'todo' : todo }

def collect_tasks():
    rows = load_rows()
    return select_tasks(datetime.now(), rows)

if __name__ == '__main__':
    tasks = collect_tasks()
    for task in tasks['todo']:
        send_email(task['email'], task['subject'], task['body'])
        time.sleep(2)
