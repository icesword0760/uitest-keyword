import unittest
from selenium import webdriver
from interpret import Interpret

class TestCase(object):
    def __init__(self):
        self.driver = webdriver
        self.interpret = Interpret()
        self.casename = ''
        self.actions = []
        self.testcases = []
        self.case_factroy()

    def init_context(self):
        self.casename = ''
        self.actions = []

    def case_factroy(self):
        for case in self.interpret.testcases:
            casename = case['casename']
            actions = case['actions']
            self.bind_actions(actions)
            self.bind_casename(casename)
            classname = casename.upper()
            testcase = type(classname, (unittest.TestCase,), {casename:run_action,
                                                              'actions':actions,
                                                              'driver':self.driver,
                                                              'tearDown':teardown,
                                                              'setUp':setup},)
            self.testcases.append(testcase(casename))
            self.init_context()

    def bind_actions(self, actions):
        self.actions=actions

    def bind_casename(self, casename):
        self.casename = casename

def run_action(self):
    for action in self.actions:
        for func, parmeters in action.items():
            func(*parmeters)

def teardown(self):
    self.driver.close()

def setup(self):
    self.driver = webdriver.Chrome()
    self.driver.maximize_window()
    Interpret.replace_driver(self.actions, self.driver)


