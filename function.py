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

def switch_to_last_handles(driver):
    """
    在打开的窗口里选择最后一个
    :return:None
    """
    all_handles = driver.window_handles
    driver.switch_to_window(all_handles[-1])

def switch_to_another_hanles(now_handle,driver):
    """
    只适用于打开两个窗口的情况，传入现在的窗口句柄后，选择另一个窗口
    :param now_handle:现在的窗口句柄
    :return:
    """
    all_handles = driver.window_handles  # 得到当前开启的所有窗口的句柄
    for handle in all_handles:
        if handle != now_handle:  # 获取到与当前窗口不一样的窗口
            driver.switch_to_window(handle)

def open_url(url,driver):
    driver.get(url)

def navigate_url(url,chrome):
    chrome.Page.navigate(url=url)

def wait_time(num):
    time.sleep(num)

def element_text_has(element,str,driver):
    element =  find_element(element, driver)
    element_text = element.text
    return unittest.TestCase().assertIn(str,element_text,"元素文本不包含预期值！")

def page_text_has(str,driver,chrome):
    chrome.wait_event("Page.loadEventFired", timeout=60)
    page_text = driver.page_source
    return unittest.TestCase().assertIn(str,page_text,"页面文本不包含预期值！")

def switch_to_iframe(iframe_msg,driver):
    driver.switch_to.frame(iframe_msg)

def switch_to_default_content(driver):
    driver.switch_to_default_content()