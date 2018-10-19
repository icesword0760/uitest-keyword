# -*- coding: utf-8 -*-
import unittest
import os
from HTMLTestRunner_PY3 import HTMLTestRunner
from testcase import TestCase

def process_case():
    report_title = '用例执行报告'
    desc = '测试执行情况展示'
    report_file = r".\Report\TestResultReport.html"
    suite = unittest.TestSuite()
    suite.addTests(TestCase().testcases)
    print(suite)
    with open(report_file, 'wb') as report:
        runner = HTMLTestRunner(stream=report, title=report_title, description=desc)
        runner.run(suite)

    #runner = unittest.TextTestRunner()
    #runner.run(suite)


process_case()