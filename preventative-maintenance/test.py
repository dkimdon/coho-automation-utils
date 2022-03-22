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

    def test_task_was_done_last_year_and_needs_to_be_done_this_year_too(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done', 'body'],
                ['sub',     'd@g.com', '12',             'dec,2017',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'December 2017'}]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    def test_task_was_done_this_year_already_and_it_does_not_need_to_be_done_again_yet(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '12',             'Dec,2018', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], [])

    def test_task_was_done_last_year_but_it_is_not_time_to_do_it_yet(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '12',             'June,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 5, 1), rows)
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], [])

    ###########################
    # Multi-year period tasks #
    ###########################

    def test_task_completed_last_year_does_not_need_to_be_completed_this_year(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '60',             'Dec,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], [])

    def test_task_completed_years_ago_does_not_need_to_be_completed_this_year(self):
        rows = [[],
                ['subject',        'email',            'Month Interval', 'done',        'body'],
                ['Sanitary lines', 'brucehe@peak.org', '60',             'April, 2017', 'do sewer thing']
               ]
        tasks = select_tasks(datetime(2019, 7, 11), rows)
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], [])

    def test_task_completed_recently_need_not_be_completed_this_year(self):
        rows = [[],
                ['subject',        'email',            'Month Interval', 'done',        'body'],
                ['Sanitary lines', 'brucehe@peak.org', '60',             'April, 2017', 'do sewer thing']
               ]
        tasks = select_tasks(datetime(2019, 7, 11), rows)
        expectedTodo = []
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    def test_task_completed_years_ago_needs_to_be_completed_this_year(self):
        rows = [[],
                ['subject',        'email',            'Month Interval', 'done',        'body'],
                ['Sanitary lines', 'brucehe@peak.org', '60',             'April, 2017', 'do sewer thing']
               ]
        tasks = select_tasks(datetime(2022, 4, 11), rows)
        expectedTodo = [{'email': 'brucehe@peak.org', 'subject': 'Sanitary lines', 'body': 'do sewer thing', 'done': 'April 2017' }]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    def test_task_was_done_3_years_ago_and_now_needs_to_be_done_again(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done', 'body'],
                ['sub',     'd@g.com', '36',             'dec,2015',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'December 2015' }]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    #########################################
    # Tasks scheduled multiple times a year #
    #########################################

    def test_bi_yearly_task_completed_last_year_need_to_be_done_now(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '6',              'Sep,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 3, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'September 2017' }]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    def test_bi_yearly_task_completed_last_year_is_now_in_backlog(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '6',              'Sep,2017', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 4, 1), rows)
        expectedBacklog = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'September 2017' }]
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], expectedBacklog)

    def test_bi_yearly_task_completed_earlier_this_year_needs_to_be_done_again(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '6',              'Jun,2018', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'June 2018' }]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])

    def test_bi_yearly_task_completed_earlier_this_need_not_be_done_yet(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done',     'body'],
                ['sub',     'd@g.com', '6',              'Jun,2018', 'do it']
               ]
        tasks = select_tasks(datetime(2018, 8, 1), rows)
        self.verify_output(tasks['todo'], [])
        self.verify_output(tasks['backlog'], [])


    ###########
    # Backlog #
    ###########

    def test_task_should_have_been_done_last_month(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done', 'body'],
                ['sub',     'd@g.com', '12',             'dec,2014',     'do it']
               ]
        tasks = select_tasks(datetime(2016, 1, 1), rows)
        expectedBacklog = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'December 2014' }]
        self.verify_output(tasks['backlog'], expectedBacklog)

    def test_task_has_never_been_completed(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done', 'body'],
                ['sub',     'd@g.com', '12',             '',     'do it']
               ]
        tasks = select_tasks(datetime(2016, 1, 1), rows)
        expectedBacklog = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'never' }]
        self.verify_output(tasks['backlog'], expectedBacklog)

    # Misc tests


    def test_with_non_standard_done_column_format(self):
        rows = [[],
                ['subject', 'email',   'Month Interval', 'done', 'body'],
                ['sub',     'd@g.com', '36',             '12/12/2015',     'do it']
               ]
        tasks = select_tasks(datetime(2018, 12, 1), rows)
        expectedTodo = [{'email': 'd@g.com', 'subject': 'sub', 'body': 'do it', 'done': 'December 2015' }]
        self.verify_output(tasks['todo'], expectedTodo)
        self.verify_output(tasks['backlog'], [])


if __name__ == '__main__':
    unittest.main()

