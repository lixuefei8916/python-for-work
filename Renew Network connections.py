#-*- coding: utf-8 -*-
'''
修复网络：
重启本地连接/无线连接
重置winsock
设置DNS （振国建议：很多出差时修改了DNS，所以添加此功能）
刷新DNS
'''

import os
import sys
import time

print u'lixuefei lxf 桌面运维自动化工具'
print u'程序正在执行中，这个过程可能需要若干分钟，请您耐心等待 (注：请勿同时运行多个)\n'


dns_primary = '114.114.114.114'
dns_second = '8.8.8.8'
dns_third = '202.106.0.20'


class Network_driver(object):
	def __init__(self):
		pass

	def reset_winsock(self):
		os.system('netsh winsock reset')

	def restart_netword(self):

		commond_change_gbk_1 = u'netsh interface set interface 本地连接 disabled'.encode('gbk')
		cmd_commond1 = commond_change_gbk_1
		commond_change_gbk_2 = u'netsh interface set interface 本地连接 enabled'.encode('gbk')
		cmd_commond2 = commond_change_gbk_2
		commond_change_gbk_3 = u'netsh interface set interface 无线网络连接 disabled'.encode('gbk')
		cmd_commond1 = commond_change_gbk_1
		commond_change_gbk_4 = u'netsh interface set interface 无线网络连接 enabled'.encode('gbk')
		cmd_commond2 = commond_change_gbk_2


		print u"正在关闭本地连接..."
		os.system(cmd_commond1)

		time.sleep(6)

		print u"正在启动本地连接..."
		os.system(cmd_commond2)

		print u"开始重置无线网络连接...（若不具备无线能力，则自动跳过）"
		os.system(cmd_commond1)
		time.sleep(10)
		os.system(cmd_commond2)


class DNS(object):
	def __init__(self):
		pass

	def flushdns(self):
		print u'正在刷新DNS...'
		cmd_commond = 'ipconfig /flushdns'
		os.system(cmd_commond)

	def set_primary_dns(self,dns_primary='202.106.0.20'):
		print u'正在设置 主DNS：%s'%(dns_primary)
		commond_change_gbk_1 = u'netsh interface ip set dns name="本地连接" source=static addr=%s register=primary'.encode('gbk') %(dns_primary)
		cmd_commond1 = commond_change_gbk_1
		os.system(cmd_commond1)

	def set_second_dns(self,dns_second='202.106.196.115'):
		print u'正在设置 第二DNS：%s'%(dns_second)
		commond_change_gbk_1 = u'netsh interface ip add dns name="本地连接" addr=%s'.encode('gbk') %(dns_second)
		cmd_commond1 = commond_change_gbk_1
		os.system(cmd_commond1)


	def set_third_dns(self,dns_third='114.114.114.114'):
		print u'正在设置 第三DNS：%s'%(dns_third)
		commond_change_gbk_1 = u'netsh interface ip add dns name="本地连接" addr=%s'.encode('gbk') %(dns_third)
		cmd_commond1 = commond_change_gbk_1
		os.system(cmd_commond1)


lxf = Network_driver()
lxf.reset_winsock()
lxf.restart_netword()

lxf = DNS()
lxf.set_primary_dns()
lxf.set_second_dns()
lxf.set_third_dns()
lxf.flushdns()

print u'\n修复完成，10秒后自动退出，请重新尝试网络'
time.sleep(10)