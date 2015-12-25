#-*- coding: utf-8 -*-

'''
以无提示方式安装 Office2013（免输入序列号和点击下一步）
 [99.20用FTP下载，遍历多层目录（ftp和本地目录的创建），无提示安装]
[难点：递归多层目录 和 静默安装方式（该方式需用微软OCT制作自定义文件，放进安装目录的Updates中）]
（感谢魏忠指导递归）

'''



from ftplib import FTP 
import os
import sys
import re

ftp = FTP()

ftp_port = 21
ftp_timeout = 30
ftp_server = '192.168.xx.xx'

ftp_user = 'xxxxxx'
ftp_passwd = '******'

now_ftp_dir_list = '/'		
ftp_download_dir_name = 'SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285'

now_local_dir_list = 'c:\lxf_files\\'	


class FTP_(object):
	def __init__(self):

		self.Local_main_dir = Local_main_dir()			# 合并class，这个class专门判断文件夹是否存在，然后创建

		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout
		self.ftp_server = ftp_server

		self.ftp_user = ftp_user
		self.ftp_passwd = ftp_passwd

	def check_file(self,now_local_dir_list,name):
		path = now_local_dir_list + name 								# path = 本地路径+文件名
		if os.path.exists(path) == True:								# 如果有，则pass
			pass   #print 'pass %s' %path
		else:															# 如果没有该文件
			return self.download(now_local_dir_list,name)				# 调用 download函数去下载

	def ftp_connect(self):
		ftp.connect(self.ftp_server,self.ftp_port,self.ftp_timeout)		# 连接ftp服务器
		return self.ftp_login()

	def ftp_login(self):
		ftp.login(self.ftp_user,self.ftp_passwd)						# 登录
		#return self.dir_recursion()

	def download(self,now_local_dir_list,name):
		path = '%s%s' %(now_local_dir_list,name) 									# path = 本地路径+文件名
		print '*********************'									# 自己测试用： * = 文件夹
		print path
		f = open(path,'wb')												# 读写权限，打开该目录和文件
		filename = 'RETR '+name											# 保存ftp文件
		ftp.retrbinary(filename,f.write)								# 从FTP下载文件
		f.close()														# 关闭文件

	def dir_recursion(self,ftp_download_dir_name,now_ftp_pwd = '/',now_local_dir_list=now_local_dir_list):


		# ftp_download_dir_name是递归的next级目录， ， now_ftp_pwd是当前目录的绝对目录（从/根开始的绝对路径）
		# now_local_dir_list=now_local_dir_list	：客户端当前绝对路径，随着递归的深入，目录层数也会增加；默认是c:\ops1905\ （只有第1次递归用到根）
	
		now_ftp_pwd = '%s/%s' %(now_ftp_pwd,ftp_download_dir_name)	
		# 等号左边的now_ftp_pwd是绝对路径，一层一层加的，（/xx/xx/ + next目录）； 即：第1次是根'/想下载的主目录', 第二次'/主目录/xx',第三次'/xx/xx/xx'

		#print '\n\n %s' %now_dir_list 								# 自己测试用

		ftp.cwd(now_ftp_pwd)										# cd进ftp的绝对路径 now_dir_list（/xx/xx/xx）
		files_list = []												# 用于存放 这个目录下， 所有的文件和文件夹的列表
		ftp.dir('.',files_list.append)								# ftp.dir是查询这个目录下， 所有的文件和文件夹， 然后，用列表方式赋值给files_list
		files = [f.split(None, 8)[-1] for f in files_list if f.startswith('-')]			#提取 所有 files的文件  -r--r--r--
		dirs = [f.split(None, 8)[-1] for f in files_list if f.startswith('d')]			#提取 所有 dir文件夹	drwxr-xr-x
		now_local_dir_list = '%s%s\\' %(now_local_dir_list,ftp_download_dir_name)		# 客户端 本地目录，当前目录+next目录（c:\xx\ + next目录）
		#注：这里必须 '%s%s\\'， 绝对不能写为带空格的 '%s%s\ '， 否则安装时显示无法找到模块，其实把空格取消就行，这个问题很难发现，我是把源文件复制过来，去运行程序检测缺少文件时发现的；
		#os.mkdir(now_local_dir_list)													# 在本地创建这个目录 （本地目录 = ftp的目录，每当ftp要进入下一级目录，就先在本地创建这个目录）
		self.Local_main_dir.mkdir(now_local_dir_list)				# 调用 这个 class 这个class专门判断文件夹是否存在，然后创建
		#print '%%%%%%%%%%%%%%%%%'									# 自己测试用， % = 文件
		#print files

		for name in files:											# 注意： 文件的遍历，一定在now_local_dir_list = '%s%s\ '之后
			self.check_file(now_local_dir_list,name)				# 去 check_file函数中 去检测文件夹和文件是否存在，如果存在文件，则创建

		for name in dirs:											# 将 列表dirs 逐个列出来								
			self.dir_recursion(name,now_ftp_pwd,now_local_dir_list)	# ★★ 带着next目录，调用自己！！




class Local_main_dir(object):
	def __init__(self):
		pass

	def mkdir(self,name):
		if os.path.exists(name) == True:							# 判断目录是否存在
			pass
		else:
			os.mkdir(name)											# 如果不存在，则创建文件夹


class office2013_software(object):
	def __init__(self):
		self.path = '%s%s' %(now_local_dir_list,ftp_download_dir_name)


	def openfile(self):
		#注意：必须在 cmd 下完成命令， 不能在 windows PowerShell测试及运行
		path = '%s%s' %(now_local_dir_list,ftp_download_dir_name)
		#提示窗口安装	cmd_commond0 = r'"%s\setup.exe"' %path
		cmd_commond0 = r'"c:\lxf_files\SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285\setup.exe"'
		# [OK]r'"c:\ops1905\SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285\setup.exe"'
		print cmd_commond0
		os.system(cmd_commond0)


'''
	def check_file(self):
		#time.sleep(10)
		file_size = os.path.getsize(self.path)	
		if file_size > 24558480:				#判断文件大小，以便确认是否下载完成
			return self.openfile()				#如果下载完成，就安装
		else:
			time.sleep(10)						#没下载完成： 睡眠10秒，再次判断文件大小
			return self.check_file()
'''



lxf=Local_main_dir()												# 初始话 本地目录 对象
lxf.mkdir(now_local_dir_list)										# 创建 c:\ops1905\
lxf=FTP_()															# 初始话 FTP 对象
lxf.ftp_connect()													# FTP连接和登录
lxf.dir_recursion(ftp_download_dir_name) 							# 递归FTP下所有目录，逐层深入
ftp.quit()															# 退出FTP连接

lxf = office2013_software()
lxf.openfile()


'''
=============================================================================================
想法 + 难点

难点1：  递归多层目录(ftp目录和本地目录的创建)

难点2：  office2013的静默安装，需要用 setup.exe /admin [安装自定义工具去导出配置，这样避免手工输入 SN]
		 然后将该文件 保存在 根目录的 Updates 文件夹中保存安装程序自定义文件
		 参考 静默安装生成配置文件 https://technet.microsoft.com/zh-cn/library/cc179097.aspx

# 递归的实现
# 递归目录，自己调用自己，当发现是文件夹，就再次return回给自己(dir列表)；
# 直至最里层目录，不再有目录后，再回外层目录，然后再次递归

# 参考http://blog.chinaunix.net/uid-21516619-id-1825037.html

=============================================================================================
'''