# -*- coding: utf-8 -*-
import unittest
from HTMLTestRunner_PY3 import HTMLTestRunner
from testcase import TestCase

def process_case():
    report_title = '用例执行报告'
    desc = '测试执行情况展示'
    report_file = './Report/ExampleReport.html'
    suite = unittest.TestSuite()
    suite.addTests(TestCase().testcases)
    with open(report_file, 'wb') as report:
        runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
        runner.run(suite)

process_case()