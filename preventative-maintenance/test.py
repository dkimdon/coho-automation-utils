#!/usr/bin/env python3
import unittest
from periodic_job import select_tasks
from datetime import datetime

class TestPeriodicJob(unittest.TestCase):
    def verify_output(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for i in range(0, len(expected)):
            self.assertDictEqual(actual[i], expected[i])

    def test_basic(self):
        rows = [[],
                ['subject', 'email', 'Year start', 'Year Interval', 'Month', 'done', 'body'],
                ['this is a subject', 'd@g.com', '2000', '1', '12', '', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expected = [{'email': 'd@g.com', 'subject': 'this is a subject', 'body': 'do it' }]
        self.verify_output(tasks, expected)


if __name__ == '__main__':
    unittest.main()

