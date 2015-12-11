#-*- coding: utf-8 -*-

'''
rtx : 下载 -- > 安装 --> [未实现:自动配置服务器IP]

暂且使用 ftplib标准库， 后续自己学习用socket写下载tfp
有关 FTP （文件传输协议） 的详细信息，参阅互联网 RFC 959

'''

from ftplib import FTP
import os
import sys
import time

#想下载的文件
download_file = 'rtxclient2011formal.exe'

ftp = FTP()

ftp_server = '192.168.xx.xx'
ftp_port = 21
ftp_timeout = 30

ftp_user = 'username'
ftp_passwd = 'passwd'

file_dir = 'c:\myfile\\'			# 客户端本地下载目录


class Local_dir(object):
	def __init__(self):
		self.__file_dir = file_dir

	def mkdir(self):
		if os.path.exists(self.__file_dir) == True:		# 判断目录是否存在
			pass
		else:
			os.mkdir(self.__file_dir)

class FTP(object):
	def __init__(self):
		self.ftp_server = ftp_server
		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout

		self.ftp_user = ftp_user
		self.ftp_passwd = ftp_passwd

		self.path = file_dir + download_file

	def check_file(self):
		if os.path.exists(self.path) == True:
			pass
		else:
			return self.ftp_connect()

	def ftp_connect(self):
		ftp.connect(self.ftp_server,self.ftp_port,self.ftp_timeout)	# 连接ftp服务器
		return self.ftp_login()

	def ftp_login(self):
		ftp.login(self.ftp_user,self.ftp_passwd)	# 登录
		return self.download()

	def download(self):
		f = open(self.path,'wb')				# 读写权限，打开该目录和文件
		filename = 'RETR '+download_file		# 保存ftp文件
		ftp.retrbinary(filename,f.write)		# 从FTP下载文件
		ftp.quit()		

class rtx_software(object):
	def __init__(self):
		self.path = file_dir + download_file

	def check_file(self):
		#time.sleep(10)
		file_size = os.path.getsize(self.path)	
		if file_size > 24558480:				#判断文件大小，以便确认是否下载完成
			return self.openfile()				#如果下载完成，就安装
		else:
			time.sleep(10)						#没下载完成： 睡眠10秒，再次判断文件大小
			return self.check_file()

	def openfile(self):
		cmd = '%s /S' %self.path				# /S 是参数： 静默安装 | /? 是查询参数
		os.system(cmd)

lxf=Local_dir()
lxf.mkdir()
lxf = FTP()
lxf.check_file()
lxf = rtx_software()
lxf.check_file()


