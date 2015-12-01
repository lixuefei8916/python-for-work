# -*- coding: utf-8 -*-
import os			#用于 os.mkdir
import time			#用于时间戳time.strftime
import datetime		#用于时间戳time.strftime
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import hashlib


#程序说明
#创建备份目录：用当日日期创建文件夹，用于把文件copy过来
#判断文件夹是否创建成功
#判断winrar是否正常
#用winrar 把 备份目录打包
#判断 今日zip大小 < 昨日zip大小
#生成md5

time = int(time.strftime('%Y%m%d'))
lasttime = int(time - 1)

#备份目录（以时间命名）
backup_dir = r'd:\python\{0}'.format(time)  
# 以系统时间(年/月/日)为名称，创建文件夹；年月日生成方法见上面 time = time.strftime('%Y%m%d')
source_dir = r'D:\python'

#以copy方式 需要复制的文件
source_file = (r'D:\python\test\rtx\*.* ',r'D:\python\1')

zip_software_dir = r'C:\Program Files\WinRAR'	#需要检测 winrar目录
zip_file = "%s\%s.rar" %(source_dir,time)
last_time_zip_file = "%s\%s.rar" %(source_dir,lasttime)


def sendmail(message):
	to_mail = "xuefei.li@xxxx.com"
	send_mail = "xuefei.li@xxxxx.com"
	mail_host = "mail.xxxxx.com"
	mail_user = "xuefei.li"
	mail_pwd = "---------"
	mail_postfix = "xxxxx.com"

	message = "%s Backup Warning: %s" %(time,detail)
	msg = MIMEText(message)

	smtp = smtplib.SMTP()
	smtp.connect('mail.xxxxxx.com')
	smtp.login(mail_user,mail_pwd)
	smtp.sendmail(to_mail,send_mail,msg.as_string())
	smtp.quit()


def mkdir_backup_dir(dir):			#创建一个函数
	dir = backup_dir     			#传一个参数进来， 参数是函数外的那个 目录
	print backup_dir
	os.mkdir(dir)					# os.mkdir 创建目录
	detail = "Make backup_dir False"		#如果需要报错，该行为传递 报错信息，给函数参数
	return check_dir(dir,detail)		# 把目录（dir = backup_dir） 传给 目录测试函数，参数是dir目录

def check_dir(dir,detail):			#测试目录是否存在
	x = os.path.exists(dir)			# os.path.exists 用于测试目录  dir = 路径
	print x
	if x == True:
		print "111111"				#如果正确 什么都不做
	else:
		sendmail(detail) 			#如果检测未有该目录，调用发送mail函数，传参detail=报错信息

def test_zip():						# 测试zip
	zip_test_detail='Can not fond Zip'		#如果需要报错，该行为传递 报错信息，给函数参数
	return check_dir(zip_software_dir,zip_test_detail)		#调用 测试目录函数，传递zip目录和报错信息


def copyfiles_to_backupdir(backup_dir,*arg):		# copy指定文件 到 备份目录下 | *arg可以传递元组=多目录下的文件一起传
	for x in source_file:		# 这个循环是 将元组，捉个换行并copy，例子：('a','b','c') 经过循环，变为 a回车 ，b回车，  c回车 
		copy_commond = " copy %s %s" %(x,backup_dir)   # windows cmd命令： copy A目录文件 到 B目录
		os.system(copy_commond) 


def use_zip():			#用rar把 备份目录打包
	zip_commond0 = r"%s" %(zip_software_dir)
	zip_commond1 = r'"%s\Rar.exe" a -k -r -s -m1 %s\%s.rar %s ' %(zip_software_dir,source_dir,time,backup_dir)   
	#换成 windows语言 = “c:\Program Files\WinRAR\Rar.exe" a -k -r -s -m1 d:\python\20150920\20150920.rar D:\python\1
	os.system(zip_commond0),
	os.system(zip_commond1)


def check_zip_size():				#检查压缩包大小， 如果比昨天小，则mail报错
	x = os.path.getsize(zip_file)					#x = 今天压缩包大小
	y = os.path.getsize(last_time_zip_file)			#y = 昨天压缩包大小
	#print "Thie Zip file size is %s" %x
	#print "Thie Zip file size is %s" %y
	if x < y:										#如果今天的zip 小于 昨天的， 那么发送mail报警
		detail = "the size just %sB today ,the zip file is litter than yesterday"%x   # 报警信息
		sendmail(detail)							# 调用 sendmail函数，并传递“报错信息”
	else:
		pass

def check_md5():									#检查md5
	md5_source = zip_file    								#md5文件存放位置
	md5_temp = r'D:\python\{0}\md5_temp.txt'.format(time)	# md5.txt的文件名
	md5file = open(md5_source,'rb')							
	md5 = hashlib.md5(md5file.read()).hexdigest()			
	md5file.close()

	md5_check_file = open(md5_temp,'w')
	md5_check_file.write(md5)
	md5_check_file.close()


mkdir_backup_dir(backup_dir)
test_zip()
copyfiles_to_backupdir(backup_dir,source_file)
use_zip()
check_zip_size()
check_md5()