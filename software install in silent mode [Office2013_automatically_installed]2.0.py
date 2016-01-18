#-*- coding: utf-8 -*-

'''
以无提示方式安装 Office2013（免输入序列号,点"下一步"）
 [192.168.*。*用FTP下载，遍历多层目录（ftp和本地目录的创建），无提示安装]
[难点：递归多层目录 和 静默安装方式（该方式需用微软OCT制作自定义文件，放进安装目录的Updates中）]
（感谢魏忠指导递归）


office : 创建目录 -- FTP下载 -- > 静默无提示式安装
sql : 运行程序时，记录mac和时间 --> select出id --> 当创建目录成功，update 1 --> FTP下载1个文件，update + 1 --> 安装成功  程序结束时间；

执行一步，记录一次step code，
第一次insert后，还要select到该id，然后主程序每执行一步，都update到这个id记录中的 detail字段（日志详细 字段）
【解决第一版问题： 当程序完成时再执行sql的insert，但若程序中途故障，导致不会执行到mysql insert，也就看不到日志了】

================================================================================
mysql update 步骤(确保准确记录故障点)：
class pc_ (记录 mac，程序开始时间、程序结束时间)
class sql_ 

lxf1 = pc_()
lxf1.get_mac()
lxf1.get_time_start()

lxf2 = sql_()
lxf.insert(mac=xx,time_start=xx)  	【注：这里id不指定，按照mysql字段要求，自增且唯一】
lxf.select(time_start=xx)			【查询到 id，以便之后往这条sql中insert】

helpdesk__主程序(第一步)
lxf.update(,detail_log = 1 ) where id=xx

helpdesk__主程序(第二步)
lxf.update(detail_log = 2 ) where id=xx

helpdesk__主程序(第n步)
lxf.update(detail_log = n ) where id=xx

lxf.update(time_end = xx ) where id=xx
【time_end 记录该程序完成时间，若有该记录，则表示程序执行成功(至于响应者问题是否解决另议)】
'''



import os
import sys
import uuid
import time
from ftplib import FTP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select,text
from sqlalchemy import func, or_, not_,and_

# 想下载的目录 / 遍历的起始目录（FTP根：/） | 本地下载存放目录(根：c:\lixuefei\)
ftp_download_dir_name = 'SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285'
now_ftp_dir_list = '/'		
now_local_dir_list = 'c:\lixuefei\\'	


# FTP初始化
ftp = FTP()
ftp_port = 21
ftp_timeout = 300
ftp_server = '192.168.*.*0'
ftp_user = 'lixuefei'
ftp_passwd = '********'

#mysql初始化数据库
sql_name = 'mysql'
sql_user = 'lixuefei'
sql_passwd = '******'
sql_host = '192.168.*.*'
database_name = 'helpdesk' 
Base = declarative_base()



class Local_main_dir(object):
	def __init__(self):
		self.sql__ = Sql_Statement()								# 执行 mysql update时用

	def mkdir(self,name):
		if os.path.exists(name) == True:							# 判断目录是否存在
			self.sql__.update_details(id=sql_id,details=1)
		else:
			os.mkdir(name)											# 如果不存在，则创建文件夹
			self.sql__.update_details(id=sql_id,details=1)


class FTP_(object):
	def __init__(self):

		self.Local_main_dir = Local_main_dir()			# 合并class，这个class专门判断文件夹是否存在，然后创建

		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout
		self.ftp_server = ftp_server

		self.ftp_user = ftp_user
		self.ftp_passwd = ftp_passwd

		self.sql__ = Sql_Statement()								# 执行 mysql update时用
		self.details = 2 											# 用于统计下载数量，总共为xxxx个，从2计算是因为创建目录已经完成

	def check_file(self,now_local_dir_list,name):
		path = now_local_dir_list + name 								# path = 本地路径+文件名
		if os.path.exists(path) == True:								# 如果有，则pass
			self.details = self.details + 1
			self.sql__.update_details(id=sql_id,details=self.details)	#不操作，但mysql里记录该操作成功
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
		self.details = self.details + 1
		self.sql__.update_details(id=sql_id,details=self.details)	#不操作，但mysql里记录该操作成功

	def dir_recursion(self,ftp_download_dir_name,now_ftp_pwd = '/',now_local_dir_list=now_local_dir_list):


		# ftp_download_dir_name是递归的next级目录， ， now_ftp_pwd是当前目录的绝对目录（从/根开始的绝对路径）
		# now_local_dir_list=now_local_dir_list	：客户端当前绝对路径，随着递归的深入，目录层数也会增加；默认是c:\lixuefei\ （只有第1次递归用到根）
	
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




class office2013_software(object):
	def __init__(self):
		self.path = '%s%s' %(now_local_dir_list,ftp_download_dir_name)
	
	def openfile(self):
		#注意：必须在 cmd 下完成命令， 不能在 windows PowerShell测试及运行
		path = '%s%s' %(now_local_dir_list,ftp_download_dir_name)
		#提示窗口安装	cmd_commond0 = r'"%s\setup.exe"' %path
		cmd_commond0 = r'"c:\lixuefei\SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285\setup.exe"'
		# [OK]r'"c:\lixuefei\SW_DVD5_Office_Professional_Plus_2013_64Bit_ChnSimp_MLF_X18-55285\setup.exe"'
		print cmd_commond0
		details = os.system(cmd_commond0)


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



class pc_(object):
	def __init__(self):
		self.detail_log = []

	def get_mac(self): 
		mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
		return ":".join([mac[e:e+2] for e in range(0,11,2)])

	def get_start_time(self):
		time_start = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
		return time_start

	def get_end_time(self):
		time_end = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
		return time_end


class Table_Office2013_automatically_installed(Base):
	__tablename__ = 'Office2013_automatically_installed'		#mysql Talbe名称，1个exe文件对应1个表
	#表结构
	#CREATE TABLE Office2013_automatically_installed(id INT PRIMARY KEY AUTO_INCREMENT,mac VARCHAR(17),time_start VARCHAR(255),time_end VARCHAR(255),details VARCHAR(255));
	id = Column(Integer,primary_key=True)
	mac = Column(String(17))
	time_start = Column(String(255))
	time_end = Column(String(255))
	details = Column(String(255))

	def __repr__(self):
		return "<Office2013_automatically_installed(id='%s',mac='%s',time_start='%s',time_end='%s',details='%s')>" %(self.id,self.mac,self.time_start,self.time_end,self.details)

class Sql_Statement(object):
	def __init__(self):
		# db = create_engine('mysql://root:*****@192.168.*.*')
		self.__database_login_commond = '%s://%s:%s@%s' %(sql_name,sql_user,sql_passwd,sql_host)
		self.__database_name = 'USE %s' %(database_name)

		db = create_engine(self.__database_login_commond)
		db.execute(self.__database_name)
		Session = sessionmaker(bind=db)
		self.session = Session()

	#只填写某字段,未填写部分 “NULL”  : INSERT INTO example2(id,course)VALUES(4,44); 
	#INSERT INTO Office2013_automatically_installed(time_start)VALUES('2016.01.13 14:33:20');
	def insert_(self,id=None,mac=None,time_start=None,time_end=None,details=None):		#把默认值 = None,只需要传需要的参数即可
		sql_table = Table_Office2013_automatically_installed(id=id,mac=mac,time_start=time_start,time_end=time_end,details=details)
		self.session.add(sql_table)
		self.session.commit()	

	def select_id(self,time_start,mac):		#利用time_start和mac组合条件， .first()是提取第1行（因为该机器在x分x秒最快也只会运行1个工具，所以暂定查询结果只有1行）
		sql_id = self.session.query(Table_Office2013_automatically_installed).filter(and_(Table_Office2013_automatically_installed.time_start==time_start,Table_Office2013_automatically_installed.mac==mac)).first().id #.id是只要 id结果，其他不显示
		return sql_id

	def update_details(self,id=None,mac=None,time_start=None,time_end=None,details=None):
		id = sql_id
		#self.session.query(Table_Office2013_automatically_installed).filter(Table_Office2013_automatically_installed.id == sql_id).update({Table_Office2013_automatically_installed.details:details}or{Table_Office2013_automatically_installed.time_end:time_end})
		#上面那种方式是错误的， 因为 detail和time_end 两个字段不会同时更新，只能1个1个更新，所以当更新time_end时，会吧details原值抹去，改为null
		# 还是拆开更新吧
		self.session.query(Table_Office2013_automatically_installed).filter(Table_Office2013_automatically_installed.id == sql_id).update({Table_Office2013_automatically_installed.details:details})

	def update_tiem_end(self,id=None,mac=None,time_start=None,time_end=None,details=None):
		id = sql_id
		self.session.query(Table_Office2013_automatically_installed).filter(Table_Office2013_automatically_installed.id == sql_id).update({Table_Office2013_automatically_installed.time_end:time_end})




# =============================================================================
print u'lxf桌面运维辅助工具 - Rtx自动化安装'
print u'程序正在执行中，这个过程可能需要若干分钟，请您耐心等待 (注：请勿同时运行多个)\n'

# 一、 程序即将开始执行， 记录使用者机器的 mac 和 时间（精确到秒）
lxf1 = pc_()
mac = lxf1.get_mac()
start_time = lxf1.get_start_time()

# 二、insert  mac 和 开始时间
lxf2 = Sql_Statement()
lxf2.insert_(mac=mac,time_start=start_time)

# 三、查询id，以便之后往这条sql中update
sql_id = lxf2.select_id(start_time,mac)


# 四、office2013自动安装主体程序执行
print u'正在创建本地下载目录... \n'
lxf=Local_main_dir()												# 初始话 本地目录 对象
lxf.mkdir(now_local_dir_list)										# 创建 c:\lixuefei\
print u'正在下载office2013安装程序(912MB)，根据网速的影响，也许需要若干分钟，请稍候... \n'
lxf=FTP_()															# 初始话 FTP 对象
lxf.ftp_connect()													# FTP连接和登录
lxf.dir_recursion(ftp_download_dir_name) 							# 递归FTP下所有目录，逐层深入
ftp.quit()															# 退出FTP连接
print u'正在安装office2013(912MB),也许需要若干分钟，请稍候..... '
print u'注：若弹出 office2013安装窗口，请点击“安装”或“下一步”\n '
lxf = office2013_software()
lxf.openfile()


#五、记录程序 结束时间
lxf1 = pc_()
end_time = lxf1.get_end_time()
lxf2 = Sql_Statement()
lxf2.update_tiem_end(id=sql_id,time_end=end_time)

# 六、完成退出
print u'安装完成，10秒后自动退出'
time.sleep(10)




'''
=============================================================================================
想法 + 难点

难点1：  递归多层目录(ftp目录和本地目录的创建)

难点2：  office2013的静默安装，需要用 setup.exe /admin [安装自定义工具去导出配置，这样避免手工输入 SN]
		 然后将该文件 保存在 根目录的 Updates 文件夹中保存安装程序自定义文件
		 参考 静默安装生成配置文件 https://technet.microsoft.com/zh-cn/library/cc179097.aspx

# 递归的实现（感谢魏忠指导 2015.12.23 11：30）
# 递归目录，自己调用自己，当发现是文件夹，就再次return回给自己(dir列表)；
# 直至最里层目录，不再有目录后，再回外层目录，然后再次递归

# 参考http://blog.chinaunix.net/uid-21516619-id-1825037.html

=============================================================================================
'''