#!/usr/bin/env python3
import unittest
from periodic_job import select_tasks
from datetime import datetime

class TestPeriodicJob(unittest.TestCase):
    def verify_output(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for i in range(0, len(expected)):
            self.assertDictEqual(actual[i], expected[i])

    # task was done last year, needs to be done this year, too
    def test_empty_done(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done', 'body'],
                ['sub',     'd@g.com', '1',             'dec',   'dec,2017',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expected = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it' }]
        self.verify_output(tasks, expected)

    # This task was completed last year and doesn't need to be completed this year
    def test_yearly_task_needs_to_be_done(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done',     'body'],
                ['sub',     'd@g.com', '5',             'Dec',   'Dec,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expected = []
        self.verify_output(tasks, expected)


if __name__ == '__main__':
    unittest.main()

