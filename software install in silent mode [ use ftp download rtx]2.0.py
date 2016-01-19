#-*- coding: utf-8 -*-

'''
第二版
2016.01.13

rtx : 创建目录 -- FTP下载 -- > 静默无提示式安装
sql : 运行程序时，记录mac和时间 --> select出id --> 当创建目录成功，update 1 --> FTP下载成功，update 2 --> 安装成功 update 3 和 程序结束时间；

执行一步，记录一次step code，
第一次insert后，还要select到该id，然后主程序每执行一步，都update到这个id记录中的 detail字段（日志详细 字段）
【解决第一版问题： 当程序完成时再执行sql的insert，但若程序中途故障，导致不会执行到mysql insert，也就看不到日志了】

================================================================================
程序步骤：
class pc_ (记录 mac，程序开始时间、程序结束时间)
class sql_ 

lxf1 = pc_()
lxf1.get_mac()
lxf1.get_time_start()

lxf2 = sql_()
lxf.insert(mac=xx,time_start=xx)  	【注：这里id不指定，按照mysql字段要求，自增且唯一】
lxf.select(time_start=xx)			【查询到 id，以便之后往这条sql中insert】

helpdesk1__主程序(第一步)
lxf.update(,detail_log = 1 ) where id=xx

helpdesk__主程序(第二步)
lxf.update(detail_log = 2 ) where id=xx

helpdesk__主程序(第n步)
lxf.update(detail_log = n ) where id=xx

lxf.update(time_end = xx ) where id=xx
【time_end 记录该程序完成时间，若有该记录，则表示程序执行成功(至于响应者问题是否解决另议)】

'''

from ftplib import FTP
import os
import sys
import uuid
import time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select,text
from sqlalchemy import func, or_, not_,and_

#想下载的文件
download_file = 'rtxclient2011formal.exe'
file_dir = 'c:\lixuefei\\'			# 客户端本地下载目录

# FTP初始化
ftp = FTP()
ftp_server = '192.168.*.*'
ftp_port = 21
ftp_timeout = 30
ftp_user = 'lixuefei'
ftp_passwd = '*****'


#mysql初始化数据库
sql_name = 'mysql'
sql_user = 'lixuefei'
sql_passwd = '*****'
sql_host = '192.168.*.*'
database_name = 'helpdesk' 
Base = declarative_base()


class Local_dir(object):
	def __init__(self):
		self.__file_dir = file_dir
		self.sql__ = Sql_Statement()

	def mkdir(self):
		if os.path.exists(self.__file_dir) == True:		# 判断目录是否存在
			self.sql__.update_details(id=sql_id,details=1)
		else:
			os.mkdir(self.__file_dir)
			self.sql__.update_details(id=sql_id,details=1)

class FTP(object):
	def __init__(self):
		self.ftp_server = ftp_server
		self.ftp_port = ftp_port
		self.ftp_timeout = ftp_timeout

		self.ftp_user = ftp_user
		self.ftp_passwd = ftp_passwd

		self.path = file_dir + download_file

		self.sql__ = Sql_Statement()			# 执行 mysql update时用

	def check_file(self):
		if os.path.exists(self.path) == True:
			self.sql__.update_details(id=sql_id,details=2)	#不操作，但mysql里记录该操作成功
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
		self.sql__.update_details(id=sql_id,details=2)	#下载完成，mysql里记录2，表示该操作成功

class rtx_software(object):
	def __init__(self):
		self.path = file_dir + download_file

		self.sql__ = Sql_Statement()			# 执行 mysql update时用

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
		print cmd
		os.system(cmd)
		self.sql__.update_details(id=sql_id,details=3)  #安装，mysql里记录3，表示该操作成功


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


class Table_rtx_automatically_installed(Base):
	__tablename__ = 'rtx_automatically_installed'		#mysql Talbe名称，1个exe文件对应1个表
	#表结构
	#CREATE TABLE rtx_automatically_installed(id INT PRIMARY KEY AUTO_INCREMENT,mac VARCHAR(17),time_start VARCHAR(255),time_end VARCHAR(255),details VARCHAR(255));
	id = Column(Integer,primary_key=True)
	mac = Column(String(17))
	time_start = Column(String(255))
	time_end = Column(String(255))
	details = Column(String(255))

	def __repr__(self):
		return "<rtx_automatically_installed(id='%s',mac='%s',time_start='%s',time_end='%s',details='%s')>" %(self.id,self.mac,self.time_start,self.time_end,self.details)

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
	#INSERT INTO rtx_automatically_installed(time_start)VALUES('2016.01.13 14:33:20');
	def insert_(self,id=None,mac=None,time_start=None,time_end=None,details=None):		#把默认值 = None,只需要传需要的参数即可
		sql_table = Table_rtx_automatically_installed(id=id,mac=mac,time_start=time_start,time_end=time_end,details=details)
		self.session.add(sql_table)
		self.session.commit()	

	def select_id(self,time_start,mac):		#利用time_start和mac组合条件， .first()是提取第1行（因为该机器在x分x秒最快也只会运行1个工具，所以暂定查询结果只有1行）
		sql_id = self.session.query(Table_rtx_automatically_installed).filter(and_(Table_rtx_automatically_installed.time_start==time_start,Table_rtx_automatically_installed.mac==mac)).first().id #.id是只要 id结果，其他不显示
		return sql_id

	def update_details(self,id=None,mac=None,time_start=None,time_end=None,details=None):
		id = sql_id
		#self.session.query(Table_rtx_automatically_installed).filter(Table_rtx_automatically_installed.id == sql_id).update({Table_rtx_automatically_installed.details:details}or{Table_rtx_automatically_installed.time_end:time_end})
		#上面那种方式是错误的， 因为 detail和time_end 两个字段不会同时更新，只能1个1个更新，所以当更新time_end时，会吧details原值抹去，改为null
		# 还是拆开更新吧
		self.session.query(Table_rtx_automatically_installed).filter(Table_rtx_automatically_installed.id == sql_id).update({Table_rtx_automatically_installed.details:details})

	def update_tiem_end(self,id=None,mac=None,time_start=None,time_end=None,details=None):
		id = sql_id
		self.session.query(Table_rtx_automatically_installed).filter(Table_rtx_automatically_installed.id == sql_id).update({Table_rtx_automatically_installed.time_end:time_end})


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

#四、rtx自动安装主体程序执行
print u'正在创建本地下载目录... \n'
lxf=Local_dir()
lxf.mkdir()				# 创建目录 - 若成功，mysql details字段记录为1，表示创建目录成功
print u'正在下载rtx安装程序(23.4MB)，根据网速的影响，也许需要若干分钟，请稍候... \n'
lxf = FTP()
lxf.check_file()		# 创建目录 - 若成功，mysql details字段记录为2，表示文件下载成功
print u'正在安装... \n'
lxf = rtx_software()	
lxf.openfile()			# 安装完成 - 若成功，mysql details字段记录为3，表示文件下载成功

#五、记录程序 结束时间
lxf1 = pc_()
end_time = lxf1.get_end_time()
lxf2 = Sql_Statement()
lxf2.update_tiem_end(id=sql_id,time_end=end_time)

# 六、完成退出
print u'安装完成，10秒后自动退出'
time.sleep(10)
