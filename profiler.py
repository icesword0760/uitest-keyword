import test
import requests
import copy
import pickle

class ProfilerResultTemplet(object):
    """
    模板类，主要放置生成覆盖率网页的模板
    """

    MINTEMPLET = r"""<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    </head>
    <body>
        <script language="javascript" type="text/javascript">
            function showdetail(pid){
                var div_pre = document.getElementsByClassName('covstyle')
                console.log(div_pre)
                for (var i=0;i<div_pre.length;i++){
                    if (div_pre[i].id != pid){
                        div_pre[i].style.display = "none"
                    }else{
                        div_pre[i].style.display = "block"
                    }
                }
            }
        </script>
        <table border="1">
            <tr>
                <th>js名称</th>
                <!--<th>覆盖率统计情况</th>-->
            </tr>
            %(jslist)s
        </table>
        <div id='pre'>
        %(pre)s
        </div> 

    </body> 

    </html>
   
    """
    JSLISTTEMPLET = r"""<tr> <td><a href="javascript:;" onclick="showdetail(%(pid)s)">%(js_name)s</a></td>  </tr> """

    CODETEMPLET = r"""<pre id="%(pid)s" class="covstyle" style="display:none;">
    %(code_data)s 
    </pre>"""

class Profiler(ProfilerResultTemplet):

    def merge_same_func_ranges(self, covdata):
        """
        当一个js的覆盖率数据包含多个相同的被统计函数时，合并这些被统计函数的覆盖率数据（ranges）
        :param covdata:过滤掉不需要域名和已覆盖函数的覆盖率数据
        :return: covdata:合并完的统计数据，该数据不会存在一个js文件含有多个相同名称函数的情况了
        """
        copy_cov = copy.deepcopy(covdata)
        for index,data in enumerate(covdata):
            for function in data['functions']:
                functionName = function['functionName']
                function_ranges = [func['ranges'] for func in copy_cov[index]['functions'] if functionName == func['functionName']]
                if len(function_ranges) > 1:
                    function_ranges = [range for ranges in function_ranges for range in ranges]
                    ranges = self.by_rule_merge_ranges(function_ranges)
                    function_item = {
					'functionName': functionName,
					'ranges': ranges,
					'isBlockCoverage': False
				    }
                    list(map(lambda func: copy_cov[index]['functions'].remove(func),[func for func in covdata[index]['functions'] if functionName == func['functionName']]))
                    copy_cov[index]['functions'].append(function_item)
        return copy_cov

    def by_rule_merge_ranges(self,list):
        """
        当传入坐标数组时，将数组内的坐标转换为唯一坐标（即 既不包含（或者被包含）其他坐标，也不能和其他坐标连续的坐标）
        :param list:传入的坐标数组
        :return:转换后的坐标数组
        """
        merge_list = []
        def _merge(ranges):
            copy_ranges = copy.deepcopy(ranges)
            ranges_length = len(ranges) - 1
            start_offset = copy_ranges[0]['startOffset']
            end_offset = copy_ranges[0]['endOffset']
            for j in range(ranges_length):
                if j < ranges_length:
                    next_start_offset = ranges[j + 1]['startOffset']
                    next_end_offset = ranges[j + 1]['endOffset']
                    if start_offset <= (
                        next_end_offset + 1) and start_offset >= next_start_offset and end_offset >= next_end_offset:
                        start_offset = next_start_offset
                        copy_ranges.remove(ranges[j + 1])
                    elif end_offset >= (
                        next_start_offset - 1) and end_offset <= next_end_offset and start_offset <= next_start_offset:
                        end_offset = next_end_offset
                        copy_ranges.remove(ranges[j + 1])
                    elif start_offset >= next_start_offset and end_offset <= next_end_offset:
                        start_offset = next_start_offset
                        end_offset = next_end_offset
                        copy_ranges.remove(ranges[j + 1])
                    elif start_offset <= next_start_offset and end_offset >= next_end_offset:
                        copy_ranges.remove(ranges[j + 1])
            copy_ranges.remove(copy_ranges[0])
            merge_list.append({
                'startOffset': start_offset,
                'endOffset': end_offset,
                'count': 0
            })
            if len(copy_ranges) == 0:
                return
            else:
                _merge(copy_ranges)
        _merge(list)
        return merge_list

    def cov_domain_filter(self, covdata, domains):
        """
        过滤统计结果，只保留含有指定域名称的js统计结果
        :param covdata: 覆盖率统计结果
        :param domains: 指定的域名称
        :return: 过滤后的统计结果
        """
        covdata = covdata['result']['result']
        cov_filter_datas = []
        if domains:
            for data in covdata:
                for domain in domains:
                    if domain in data['url']:
                        cov_filter_datas.append(data)
            return cov_filter_datas
        else:
            return covdata

    def cov_not_count_filter(self, covdata):
        """
        过滤统计结果，只保留未被覆盖到的函数统计结果
        :param covdata: cov_domain_filter()后的覆盖率统计结果
        :return: 过滤后的统计结果
        """
        copy_cov = copy.deepcopy(covdata)
        #如果是被覆盖到函数，则移除该函数的统计数据
        for index,data in enumerate(covdata):
            for f_index,function in enumerate(data['functions']):
                for range in function['ranges']:
                    if range['count'] is not 0:
                        copy_cov[index]['functions'][f_index]['ranges'].remove(range)
        covdata = copy.deepcopy(copy_cov)
        #如果某函数统计数据为空，则移除该函数
        for index,data in enumerate(copy_cov):
            for function in data['functions']:
                if len(function['ranges']) == 0:
                    covdata[index]['functions'].remove(function)
        return covdata

    def code_html_filter(self, codedata):
        """
        转义js代码里的html标签防止干扰展示
        :param codedata: 待转义的js代码
        :return: 转义后的js代码
        """
        codedata = codedata.replace("<", "&lt")
        codedata = codedata.replace(">", "&lt")
        codedata = codedata.replace("""&ltfont style="background:yellow" bgcolor="yellow"&lt""", """<font style="background:yellow" bgcolor="yellow">""")
        codedata = codedata.replace("&lt/font&lt", "</font>")
        return codedata

    def make_jslist_tmp(self, pid, url):
        """
        生成js列表部分的html模板填充方法
        :param pid: js的id
        :param url: js的url路径
        :return: 填充好的模板
        """
        jslist_tmp = self.JSLISTTEMPLET % dict(
            pid = pid,
            js_name=url
        )
        return jslist_tmp

    def make_codepre_tmp(self,pid,url,positions):
        """
        生成js代码块部分的html模板填充方法
        :param pid: 与js的id对应的id
        :param url: 获取js代码用的url
        :param positions: 未被覆盖的js的索引位置
        :return: 填充好的模板
        """
        codepre_tmp = self.CODETEMPLET % dict(
            pid=pid,
            code_data=self.insert_backgroud(self.get_js(url), positions)
        )
        return codepre_tmp

    def make_cov_profiler_temp(self, covdata):
        """
        生成最终的覆盖率模板的填充方法
        :param covdata: 覆盖率数据
        :return: 填充好的模板
        """
        jslists_tmp = ""
        codepres_tmp = ""
        for index,data in enumerate(covdata):
            if data['url'].count('.js') and len(data['functions']) > 0:
                url = data['url'].replace(' ', '')
                jslists_tmp=jslists_tmp+(self.make_jslist_tmp(index,url))
                positions = []
                for function in data['functions']:
                    for offset in function['ranges']:
                        startOffset = offset['startOffset']
                        endOffset = offset['endOffset']
                        positions.append((startOffset,endOffset))
                codepres_tmp=codepres_tmp+(self.make_codepre_tmp(index,url,positions))
        cov_profiler_temp = [jslists_tmp, codepres_tmp]
        return cov_profiler_temp

    def insert_backgroud(self, codedata, positions):
        """
        将显示未覆盖代码的背景颜色的html标签,插入原始的js代码中，未覆盖代码会有黄色背景作为展示
        【！重要的】这个方法采用了较为牺牲性能（比较懒）的插入方法，会对统计速度产生严重影响！
        :param codedata: 原始的js代码
        :param positions: 未被覆盖的js代码的索引
        :return: 插入背景色完毕的代码
        """
        sourcedata = copy.deepcopy(codedata)
        for index,position in enumerate(positions):
            codedata = list(codedata)
            count_code  = "".join(sourcedata[position[0]:position[1]])
            if len(count_code) > 0 and count_code is not " ":
                insert_complet_str = """<font style="background:yellow" bgcolor="yellow">"""+count_code+"</font>"
                codedata  = "".join(codedata)
                codedata = codedata.replace(count_code,insert_complet_str,1)
        codedata = "".join(codedata)
        codedata = self.code_html_filter(codedata)
        return codedata

    def make_profiler_report(self, covdata, stream):
        """
        生成报告的方法
        :param covdata:覆盖率数据
        :param stream:写入流
        :return:
        """
        cov_profiler_temp = self.make_cov_profiler_temp(covdata)
        templet = self.MINTEMPLET % dict(
            jslist = cov_profiler_temp[0],
            pre = cov_profiler_temp[1]
        )
        stream.write(templet.encode('utf8'))

    def get_js(self, url):
        """
        如果是本地文件则打开本地文件，不是则通过js的网络路径获取其代码
        :param url: js的网络路径
        :return: 获取到的js代码
        """
        if url.startswith('file:'):
            url_path = url[8:]
            with open(url_path, 'rb') as stream:
                js = stream.read()
                js = js.decode(encoding="utf-8")
        else:
            js = requests.get(url=url).text
        return js

    def make_covdata_file(self,cov_path,covdata,domains):
        """
        接受原始的覆盖率数据，过滤并和本地数据对比（如果没有则生成），写入本地
        【！你来你也这么多for】
        :param covdata:原始覆盖率数据
        :return:
        """
        covdata = self.merge_same_func_ranges(self.cov_not_count_filter(self.cov_domain_filter(covdata,domains)))
        try:
            with open(cov_path, 'rb') as cov_stream:
                covfile = pickle.load(cov_stream)
                covfile = self.merge_same_func_ranges(covfile)
            #如果新文件含有本地文件没有的js的统计情况，则在本地文件追加该js的统计情况
            #todo 这里jsid需要改为用jsname作为标识值
            covfile_jid = [data['scriptId'] for data in covfile]
            covdata_jid = [data['scriptId'] for data in covdata]
            difference_jid_list = [jid for jid in covdata_jid if jid not in covfile_jid]
            for item in difference_jid_list:
                for data in covdata:
                    if data['scriptId'] == item:
                        covfile.append(data)
            for item in covdata:
                scriptId = item['scriptId']
                for fileitem in covfile:
                    if fileitem['scriptId'] == scriptId:
                        #如果新文件的js统计中，有方法的统计情况和本地文件的该js的该方法的统计情况有出入，则按规则在本地文件内追加或者修改该统计情况
                        for file_func in fileitem['functions']:
                            funcname = file_func['functionName']
                            data_func_ranges = [func['ranges'] for func in item['functions'] if func['functionName'] == funcname]
                            data_func_ranges = [func_range for func_ranges in data_func_ranges for func_range in func_ranges]
                            file_func_ranges = file_func['ranges']
                            if data_func_ranges != file_func_ranges:
                                ranges = file_func_ranges + [item for item in data_func_ranges if item not in file_func_ranges]
                                ranges = self.by_rule_merge_ranges(ranges)
                                file_func['ranges'] = ranges
                        #如果新文件的js统计中，含有本地文件没有的该js的方法的统计情况，则在本地文件的该js统计中，追加该方法的统计情况
                        difference_func_list = [func for func in item['functions'] if func not in fileitem['functions'] ]
                        if difference_func_list:
                            #print(difference_func_list)
                            fileitem['functions'] = fileitem['functions']+difference_func_list
            with open(cov_path, 'wb') as cov_stream:
                pickle.dump(covfile, cov_stream)
            return covfile
        except FileNotFoundError:
            with open(cov_path, 'wb') as cov_stream:
                pickle.dump(covdata, cov_stream)
            return covdata
