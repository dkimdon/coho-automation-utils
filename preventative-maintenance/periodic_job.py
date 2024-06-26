#!/usr/bin/env python3

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import time
import re
import sys
import argparse
import pprint
import calendar

def send_email(recipients, subject, body):
    AWS_REGION = "us-west-2"
    SENDER = "CoHo Preventative Maintenance Reminder <dkimdon@gmail.com>"
    REPLY_TO = "Deb Carey <boiester@gmail.com>"
    CHARSET = "UTF-8"

    client = boto3.client('ses',region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipients,
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
                REPLY_TO,
            ],
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def send_task_email(recipients, subject, body):
    intro="""Hello,
    Thank you for being the owner of this CoHo preventative maintenance task as you are contributing to the longevity of our physical community. As the owner of the task we are asking you to do the following:
    - Do the task in the month scheduled or let Deb Carey boiester@gmail.com know when you will complete the task or if you are unable to do so.
    - When task is completed send an email back to Deb when the task was completed with the  information that should be recorded in the PM task history.
    - If the task is unclear or you need additional informational to safely complete the task please ask Bruce or David.\n
    - If the task is to be competed on a work party day you are responsible for notifying the work day coordinator and coordinating or getting assistance for your task.\n"""
    send_email(recipients, subject, intro + body)

def send_summary_email(recipients, tasks):
    subject = "Preventative Maintenance Summary: " + datetime.today().strftime('%Y-%m-%d')
    body = ''

    if len(tasks['backlog']) == 0:
        body += "There are no leftover tasks from previous months.\n"
    else:
        body += "\nUncompleted tasks from previous months:\n\n"
        for task in tasks['backlog']:
            email = task['email'] if task['email'] != '' else 'No one'
            body += "\t-%s was tasked to %s, last done %s\n" % (email, task['subject'], task['done'])

    send_email(recipients, subject, body)

def load_rows():
    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    SPREADSHEET_ID = '1EGhrt3WfEsQDmzMDjJz7jPEOxsAkEuZv-EChFjniZwk'
    RANGE_NAME = 'Buildings'

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
    currentMonth = today.month
    currentYear = today.year

    indexes = {
        "subject": None,
        "email": None,
        "month interval": None,
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
    backlog = []
    if not rows:
        print('No data found.')
    else:
        for row in rows[headerIdx+1:]:
            print('\n')
            print(row)
            if len(row) < len(indexes):
              continue
            task = {}

            task['email'] = row[indexes['email']].strip() if len(row) > indexes['email'] else ''
            task['subject'] = row[indexes['subject']].strip() if len(row) > indexes['subject'] else ''
            task['body'] = row[indexes['body']].strip() if len(row) > indexes['body'] else ''

            done = row[indexes['done']].lower().strip()
            if len(done) == 0 or done == '?':
                print("Task has never been completed")
                task['done'] = 'never'
                backlog.append(task)
                continue

            monthInterval = int(row[indexes['month interval']].strip())

            splittedDone = re.split("[\s,]+", done)
            if len(splittedDone) == 2:
                monthDone = datetime.strptime(splittedDone[0].strip().lower()[0:3], '%b').month
                yearDone = int(splittedDone[1].strip())
            else:
                splittedDone = re.split("[/]", done)
                if len(splittedDone) == 3:
                    yearDone = int(splittedDone[2].strip())
                    monthDone = int(splittedDone[0].strip())
                else:
                    # Assume all we have is a year
                    yearDone = int(splittedDone[0].strip())
                    monthDone = 12  # XXX - Assume December

            task['done'] = '%s %d' % (calendar.month_name[monthDone], yearDone)

            # todoMonthEpoc and currentMonthEpoc are in units of months since the year zero
            todoMonthEpoc = yearDone * 12 + monthDone + monthInterval
            currentMonthEpoc = currentYear * 12 + currentMonth
            if todoMonthEpoc == currentMonthEpoc:
                print("Task is due to be completed this month")
                todo.append(task)
            elif todoMonthEpoc > currentMonthEpoc:
                print("Task need not be completed yet")
            elif todoMonthEpoc < currentMonthEpoc:
                print("Task should have been completed")
                backlog.append(task) 


    return { 'todo' : todo, 'backlog': backlog }

def collect_tasks(today):
    rows = load_rows()
    return select_tasks(today, rows)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preventative maintenance email reminder.')
    parser.add_argument('--date', help='Dry-run mode using the specified DATE in YYYYMMDD format as today.')
    options = parser.parse_args()
    if options.date == None:
      tasks = collect_tasks(datetime.now())
      for task in tasks['todo']:
        if task['email'] != '':
          send_task_email([task['email']], task['subject'], task['body'])
          time.sleep(2)
      for task in tasks['backlog']:
        if task['email'] != '':
          send_task_email([task['email']], "PAST DUE: (last done %s) " % (task['done']) + task['subject'], task['body'])
          time.sleep(2)
      send_summary_email(['brucehe@peak.org', 'dkimdon@gmail.com', 'boiester@gmail.com' ], tasks)
    else:
      faketoday = datetime.strptime(options.date, '%Y%m%d')
      tasks = collect_tasks(faketoday)
      pp = pprint.PrettyPrinter(indent=4)
      pprint.pprint(tasks)

