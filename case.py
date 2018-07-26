cases =[
[
    {'name': 'test_baidu'},
    {'action': "打开网址", 'parmeters':['http://www.baidu.com/']},
    {'action':"输入", 'parmeters':["百度搜索框",'100行代码打造关键字驱动的ui自动化测试框架']},
    {'action': "点击", 'parmeters': ["百度搜索按钮"]},
    {'validate': "页面文本包含", 'parmeters': ["百度"]},
],

]
