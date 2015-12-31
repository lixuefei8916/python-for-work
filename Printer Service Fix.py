#-*- coding: utf-8 -*-
import os
import sys
import _winreg

'''
修复过程

1. 停止 spooler 服务
2. 注销 spoolsv.exe 进程
3. 清空打印列队 C:\WINDOWS\system32\spool\PRINTERS\
4. 修改打印机 Standard TCP/IP Port 地址
	控制面板 - 设备和打印机 - HP LaserJet M1530 MFP Series PCL 6 - 右键 - 打印机属性 - 端口 - HPLaserJetM1530MFP - 配置端口 - 
    printer Name or IP Address : 192.168.xx.xx
5. 开启 spooler 服务

'''
print u'1905运维人员辅助工具'
print u'程序正在执行中...（注：程序若遇到问题，请联系lxf）'


# -----------------------------------------------------------

#print '正在停止 spooler 服务' 
cmd_commond1 = 'net stop spooler'
os.system(cmd_commond1)

# -----------------------------------------------------------

print u'清空打印队列 del /f /s /q C:\WINDOWS\system32\spool\PRINTERS\*.*'
Local_print_queue_path = 'C:\WINDOWS\system32\spool\PRINTERS\\'
filenames = os.listdir(Local_print_queue_path)
for name in filenames:
	path = Local_print_queue_path + name
	print 'Del %s...' %(path)
	os.remove(path)


# -----------------------------------------------------------
#print '终止打印进程spoolsv.exe'
os.popen("ntsd -c q -pn spoolsv.exe cmd")

# -----------------------------------------------------------
# 利用注册表设置打印机端口IP
# 参考http://www.jb51.net/article/56165.htm   ython修改注册表终止360进程实例
print u'正在重置打印机设置'
#在HPLaserJetM1536dnfMFP下，创建新建值，键名字：IPAddress    值=192.168.99.200
key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control\Print\Monitors\HP Standard TCP/IP Port\Ports\HPLaserJetM1536dnfMFP",0,_winreg.KEY_WRITE)
_winreg.SetValueEx(key,"IPAddress",0,_winreg.REG_SZ,r"192.168.xx.xx")

# -----------------------------------------------------------

print u'正在开启 spooler 服务' 
cmd_commond2 = 'net start spooler'
os.system(cmd_commond2)

print u'已经修复完成，按任意建退出，可再次尝试打印'
os.system("pause") 





