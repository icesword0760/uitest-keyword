import unittest
import os
import time
import PyChromeDevTools
import config
from selenium import webdriver
from interpret import Interpret
from profiler import Profiler

class TestCase(object):
    def __init__(self):
        #self.driver = webdriver
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
                                                              #'driver':self.driver,
                                                              'tearDown':teardown,
                                                              'setUp':setup},)
            self.testcases.append(testcase(casename))
            self.init_context()

    def bind_actions(self, actions):
        self.actions=actions

    def bind_casename(self, casename):
        self.casename = casename

def retry(times):
    def retry_func(func):
        def _(*args, **kwds):
            for i in range(times):
                try:
                    func(*args, **kwds)
                    return
                except AssertionError:
                    pass
            raise AssertionError(func)
        return _
    return retry_func

@retry(3)
def run_action(self):
    for action in self.actions:
        for func, parmeters in action.items():
            func(*parmeters)

def teardown(self):
    self.chrome.wait_event("Page.loadEventFired", timeout=60)
    time.sleep(3)
    cov = self.chrome.Profiler.takePreciseCoverage()
    self.chrome.Profiler.disable()
    #res = c['result']['result']
    cov = Profiler().make_covdata_file(config.cov_data_path,cov, ["zyj"])
    report_file = config.cov_report_path
    with open(report_file, 'wb') as report:
        Profiler().make_profiler_report(stream=report, covdata=cov)
    self.driver.close()
    self.chrome.close()

def setup(self):
    #os.chdir(r"C:\Program Files (x86)\Google\Chrome\Application")
    os.chdir(config.chrome_install_path)
    cmd = "chrome.exe --remote-debugging-port=9222"
    os.popen(cmd)
    time.sleep(1)
    self.chrome = PyChromeDevTools.ChromeInterface()
    self.options = webdriver.ChromeOptions()
    self.options._debugger_address = "localhost:9222"
    self.driver = webdriver.Chrome(chrome_options=self.options)
    Interpret.replace_driver(self.actions, self.driver)
    Interpret.replace_chrome(self.actions, self.chrome)
    self.chrome.Profiler.enable()
    self.chrome.Profiler.startPreciseCoverage()



