# -*- coding: utf-8 -*-
import time
import unittest

def input(element,str,driver):
    find_element(element, driver).send_keys(str)

def click(element,driver):
    find_element(element,driver).click()

def find_element(element,driver):
    webelement = driver.find_element(*element)
    return webelement

def open_url(url,driver):
    driver.get(url)

def wait_time(num):
    time.sleep(num)

def element_text_has(element,str,driver):
    element =  find_element(element, driver)
    element_text = element.text
    return unittest.TestCase().assertIn(str,element_text,"元素文本不包含预期值！")

def page_text_has(str, driver):
    page_text = driver.page_source
    return unittest.TestCase().assertIn(str,page_text,"页面文本不包含预期值！")
