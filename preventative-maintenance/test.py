#!/usr/bin/env python3
import unittest
from periodic_job import select_tasks
from datetime import datetime

class TestPeriodicJob(unittest.TestCase):
    def verify_output(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for i in range(0, len(expected)):
            self.assertDictEqual(actual[i], expected[i])

    ################
    # Yearly tasks #
    ################

    def test_task_was_done_this_year_and_needs_to_be_done_this_year_too(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done', 'body'],
                ['sub',     'd@g.com', '1',             'dec',   'dec,2017',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it' }]
        self.verify_output(tasks['todo'], expectedTodo)

    def test_task_was_done_this_year_already_and_it_does_not_need_to_be_done_again_yet(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done',     'body'],
                ['sub',     'd@g.com', '1',             'Dec',   'Dec,2018', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = []
        self.verify_output(tasks['todo'], expectedTodo)

    def test_task_was_done_last_year_but_it_is_not_time_to_do_it_yet(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done',     'body'],
                ['sub',     'd@g.com', '1',             'Dec',   'June,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 5, 1), rows)
        expectedTodo = []
        self.verify_output(tasks['todo'], expectedTodo)

    ###########################
    # Multi-year period tasks #
    ###########################

    def test_task_completed_last_year_does_not_need_to_be_completed_this_year(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done',     'body'],
                ['sub',     'd@g.com', '5',             'Dec',   'Dec,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = []
        self.verify_output(tasks['todo'], expectedTodo)

    def test_task_was_done_3_years_ago_and_now_needs_to_be_done_again(self):
        rows = [[],
                ['subject', 'email',   'Year Interval', 'Month', 'done', 'body'],
                ['sub',     'd@g.com', '3',             'dec',   'dec,2015',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it' }]
        self.verify_output(tasks['todo'], expectedTodo)


if __name__ == '__main__':
    unittest.main()

