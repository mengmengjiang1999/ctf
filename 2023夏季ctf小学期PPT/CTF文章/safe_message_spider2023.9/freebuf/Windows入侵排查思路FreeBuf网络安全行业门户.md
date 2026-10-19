在B站看过的一个教程,现在把它记录下来(部分图片涉及我的用户名,所以打码)

### ###1.系统账号安全###

 **1.1查看服务器是否有弱口令，远程管理端口是否对公网开放。**

检查方法：据实际情况咨询相关服务器管理员。

 **1.2查看服务器是否存在可疑账号、新增账号。**

检查方法：打开 cmd
窗口，输入lusrmgr.msc命令，查看是否有新增/可疑的账号，如有管理员群组的（Administrators）里的新增账户，如有，请立即禁用或删除掉。

 **1.3查看服务器是否存在隐藏账号、克隆账号。**  
检查方法：  
a、打开注册表 ，查看管理员对应键值。  
b、使用D盾_web查杀工具，集成了对克隆账号检测的功能。![image.png](https://image.3001.net/images/20210929/1632912785_615445912d0e64ce4dc93.png!small)

 **1.4结合日志，查看管理员登录时间、用户名是否存在异常。**  
检查方法：  
a、Win+R打开运行，输入“eventvwr.msc”，回车运行，打开“事件查看器”。  
b、导出Windows日志--安全，利用日志分析工具进行分析。  
下面是一个windows下的一个日志分析工具  
Github：https://github.com/nmgwddj/logs-monitor

### ###2.异常端口、进程###

 **2.1检查端口连接情况，是否有远程连接、可疑连接。  
检查方法：**  
a. netstat -ano |findstr "ESTABLISHED" 查看目前的网络连接，定位可疑的ESTABLISHED
进程![image.png](https://image.3001.net/images/20210929/1632913505_61544861ef6b0a2634435.png!small)b.
根据netstat 定位出的pid，再通过tasklist命令进行进程定位 tasklist | findstr
“PID”![image.png](https://image.3001.net/images/20210929/1632913605_615448c52f3ccd84a603b.png!small)
**2.2 查看可疑的进程及其子进程。可以通过观察以下内容：**

没有签名验证信息的进程

没有描述信息的进程

进程的属主

进程的路径是否合法

CPU或内存资源占用长时间过高的进程

查看方法:  
a. 查看端口对应的PID：  
netstat -ano | findstr “port”  
b. 查看进程对应的PID：  
任务管理器--查看--选择列--PID 或者 tasklist | findstr “PID”  
c. 查看进程对应的程序位置：  
任务管理器--选择对应进程--右键打开文件位置  
运行输入 wmic，cmd界面 输入 process

d. tasklist /svc 进程--PID--服务

e. 查看Windows服务所对应的端口：  
%system%/system32/drivers/etc/services（一般%system%就是C:\Windows）

### ###3.启动项、计划任务、服务###

 **3.1检查启动项**

a.
登录服务器，单击【开始】>【所有程序】>【启动】，(或者win+R,之后输入"shell:startup"点击确认)默认情况下此目录在是一个空目录，确认是否有非业务程序在该目录下。

![image.png](https://image.3001.net/images/20210929/1632914522_61544c5a3297e2e54b5c4.png!small)

b. win+r输入msconfig或打开任务管理器，查看是否存在命名异常的启动项目，是则取消勾选并找到改文件并删除

c. win+r输入regedit打开注册表，查看开机启动项是否正常，特别注意如下3个注册表

◆HKEY_CURRENT_USER\software\micorsoft\windows\currentversion\run

◆HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run

◆HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Runonce  
 **3.2计划任务和自启动服务**

a. 单击【开始】>【设置】>【控制面板】>【任务计划】，查看计划任务属性，便可以发现木马文件的路径。

b. 单击【开始】>【运行】；输入
cmd，然后输入at，检查计算机与网络上的其它计算机之间的会话或计划任务，如有，则确认是否为正常连接。若at弃用则使用schtasks.exe

c. win+r输入services.msc，注意服务状态和启动类型，检查是否有异常服务

### ###4.检查系统相关信息###

 **4.1 查看系统版本以及补丁信息**  
检查方法：单击【开始】>【运行】，输入systeminfo，查看系统信息

 **4.2 查找可疑目录及文件**  
检查方法：  
a、 查看用户目录，新建账号会在这个目录生成一个用户目录，查看是否有新建用户目录。  
Window 2003 C:\Documents and Settings  
Window 2008R2 C:\Users  
b、单击【开始】>【运行】，输入%UserProfile%\Recent，分析最近打开分析可疑文件。  
c、在服务器各个目录，可根据文件夹内文件列表时间进行排序，查找可疑文件。

### ###5.自动化查杀###

 **5.1 病毒查杀**

火绒安全软件  
360杀毒  
zbot病毒查杀工具  
腾讯哈勃分析系统:https://habo.qq.com/  
VirusTotal:https://www.virustotal.com

 **5.2 webshell查杀**

D盾_Web查杀:http://www.d99net.net  
WebShellkiller:http://edr.sangfor.com.cn/backdoor_detection.html  
河马查杀:http://www.webshell.pub  
百度WebShell检测:https://scanner.baidu.com

### ###6.日志分析###

 **6.1 系统日志**  
分析方法：  
a、前提：开启审核策略，若日后系统出现故障、安全事故则可以查看系统的日志文件，排除故障，追查入侵者的信息等。  
b、Win+R打开运行，输入“eventvwr.msc”，回车运行，打开“事件查看器”。  
C、导出应用程序日志、安全日志、系统日志，利用Log Parser,Event Log Explorer,Tail for Windows 等工具进行分析。

 **6.2 WEB访问日志**

分析方法：  
a. 找到中间件的web日志，打包到本地方便进行分析。  
b. 推荐工具：Window下，推荐用 EmEditor 进行日志分析，支持大文本，搜索效率还不错。 Linux下，使用Shell命令组合查询分析

下面是一个自动化的分析工具  
网址:http://secsky.sinaapp.com  
![image.png](https://image.3001.net/images/20210929/1632915574_615450760c4b1a18b96ed.png!small)

