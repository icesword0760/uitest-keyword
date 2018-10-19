from selenium.webdriver.common.by import By
from case import cases
from elementdb import element
from keyworddb import keyword
from selenium import webdriver
import function
import inspect

class Interpret(object):
    def __init__(self):
        self.casename = ''
        self.action_list = []
        self.testcases = []
        self.testcase = {
                'casename': self.casename,
                'actions': self.action_list,
            }
        self.interpret_cases()

    def init_context(self):
        self.casename = ''
        self.action_list = []
        self.testcase = {
                'casename': self.casename,
                'actions': self.action_list,
            }

    def interpret_cases(self):
        for case in cases:
            self.interpret_case(case)
            self.bind_testcase(self.testcase)
            self.init_context()

    def interpret_case(self, case):
        for _ in case:
            for k,v in _.items():
                if k == 'name':
                    self.bind_casename(v)
                if k == 'action' or k == 'validate':
                    func_name = keyword[v]
                    func = getattr(function, func_name)
                    func_parmeters = inspect.signature(func).parameters.values()#func_parmeters是获取到的函数的参数列表
                    parmeter_list = self.interpret_parmeters(_['parmeters'],func_parmeters)
                    action = {func:parmeter_list}
                    self.bind_action_list(action)

    def interpret_parmeters(self, parmeters, func_parmeters):
        parmeter_list = []
        for parmeter in parmeters:
            parmeter_list.append(parmeter)
        # 遍历函数的参数名称集合，如果其中有element，则将该参数通过element映射关系，转换为元组数据并替换原有用例对应的参数
        for index, f_type in enumerate(func_parmeters):
            f_type = str(f_type)
            if f_type == 'element':
                element_keyword = parmeters[0]
                find_method = eval(element[element_keyword][0])
                # element_tuple为元组数据，记录了对象的查找方式和位置信息
                element_tuple = (find_method, element[element_keyword][1])
                parmeter_list[index] = element_tuple
            if f_type == 'driver':
                #print(type(self.driver))
                #parmeter_list[index] = '$Web_Driver'
                parmeter_list.append('$Web_Driver')
                #parmeter_list.append(self.driver)
            if f_type == 'chrome':
                parmeter_list.append('$Chrome_Dev')
        return parmeter_list

    @classmethod
    def replace_driver(self, actions, driver):
        for action in actions:
            for v in action.values():
                for index, _ in enumerate(v):
                    if _ == '$Web_Driver':
                        v[index] = driver

    @classmethod
    def replace_chrome(self, actions, chrome):
        for action in actions:
            for v in action.values():
                for index, _ in enumerate(v):
                    if _ == '$Chrome_Dev':
                        v[index] = chrome

    def bind_action_list(self, action):
        self.testcase['actions'].append(action)

    def bind_casename(self, name):
        self.testcase['casename'] = name

    def bind_testcase(self, case):
        self.testcases.append(case)


