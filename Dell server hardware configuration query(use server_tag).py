#-*- coding: utf-8 -*-
import os
import re
import sys
import requests
from sqlalchemy import *
import shutil
import sqlite3



Service_Tag = 'xxxxxx'
# Service_Tag = raw_input(u"请输入DELL服务编码： ".encode("GBK"))

class Dell_server(object):
	def __init__(self):
		self.__dell_url = 'http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/xxxxxx/configuration?s=BSD'
		self.__html_code = 'blank'
		self.__html_file = r'tmp.html'

		self.__cpu_detail = 'blank'
		self.__cpu_total = 'blank'

		self.__mem_detail = 'blank'
		self.__mem_total = 'blank'

		self.__disk_detail = 'blank'
		self.__disk_total = 'blank'

	def set_service_tag(self,Service_Tag):
		self.__dell_url = 'http://www.dell.com/support/home/cn/zh/cndhs1/product-support/servicetag/%s/configuration?s=BSD' %(Service_Tag)

	def requests_html(self):
		conn = requests.get(self.__dell_url)
		conn.url
		html_code = conn.text
		self.__html_code = html_code

	def download_html_code(self):
		reload(sys)							# 规定编码，无此行会报告 
		sys.setdefaultencoding( "utf-8" )	# UnicodeEncodeError: 'ascii' codec can't encode characters 
		f = file(self.__html_file,'wb')
		f.write(self.__html_code)			
 		f.close

	def search_disk_detail(self):
		pattern1 = re.compile(r'\<span\s+\w.+>\d+\</span>\s+\<sp\w.+\HARD DRIVE,.+')
		x = pattern1.search(self.__html_code)
		if x:
			disk_html_code = x.group()

		pattern2 = re.compile(r'>\d+\<')
		y = pattern2.search(disk_html_code)
		if y:
			self.__disk_total = y.group()


		pattern3 = re.compile(r'HARD DRIVE.+')
		z = pattern3.search(disk_html_code)
		if z:
			self.__disk_detail = z.group()


	def search_cpu_detail(self):
        pattern1 = re.compile(r'\<span\s+\S+\s+\S+\;">\d+\S+\s+\S+\s+\S+\s+\Processor.+')
		y = pattern1.search(self.__html_code)
		if y:
			cpu_html_code = y.group()

		pattern2 = re.compile(r'>\d+\<')
		z = pattern2.search(cpu_html_code)
		if z:
			self.__cpu_total = z.group()

		pattern3 = re.compile(r'\Processor,.+\<')
		x = pattern3.search(cpu_html_code)
		if x:
			self.__cpu_detail = x.group()
			# y是下面2行html代码
			#<span class="col-xs-3" style="text-align:center;">8</span>
        	#<span class="col-xs-5">MODULE, HARD DRIVE, 300G, SAS6, 15K, 3.5, HITACHI</span>
        	#pattern1的解释： \<span | \s+是<span后面的1个空格 | \S+:class="col-xs-3" | \s+:1个空格 | 
        	#				  \S+:style="text-align:center  | \;"> 是匹配;"> 
        	#    		      [重点]\d+：正式向要的内存数量 | \S+匹配到</span> | \S+是后面N多空格
        	#				  \S+匹配<span | \s+:1个空格 |  S+

	def search_mem_detail(self):
		pattern1 = re.compile(r'\<span\s\w.+>\d+\</span>\s+\<sp\w.+\MODULE.+\MEMORY MODULE.+')
		x = pattern1.search(self.__html_code)
		if x:
			mem_html_code = x.group()

		pattern2 = re.compile(r'>\d+\<')
		y = pattern2.search(mem_html_code)
		if y:
			self.__mem_total = y.group()


		pattern3 = re.compile(r'MEMORY.+\w+\<')
		z = pattern3.search(mem_html_code)
		if z:
			self.__mem_detail = z.group()



	def print_detail(self):
		print self.__cpu_total
		print self.__cpu_detail
		print '-------------------'
		print self.__mem_total
		print self.__mem_detail
		print '-------------------'
		print self.__disk_total
		print self.__disk_detail	
		print '-------------------'


if __name__ == '__main__':  
	lxf = Dell_server()

	lxf.set_service_tag(Service_Tag)
	lxf.requests_html()
	lxf.download_html_code()
	lxf.search_cpu_detail()
	lxf.search_mem_detail()
	lxf.search_disk_detail()
	print lxf.print_detail()
	#lxf.write_into_mysql()
