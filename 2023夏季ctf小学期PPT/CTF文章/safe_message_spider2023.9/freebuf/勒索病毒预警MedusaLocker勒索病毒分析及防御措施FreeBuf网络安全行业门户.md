# 1 恶意代码信息

名称：Trojan.DelShad.if

类型：勒索病毒

MD5：d54fa56f495571d8000ced3fefccf2a7

SHA1：e4f65eba10cc0dc840549dc3ec5212e015564b1b

文件类型：PE 32位

文件大小：676,864 字节

传播途径：无主动传播途径

影响系统：windows xp及以上

# 2 恶意代码概况

近日，江民赤豹安全实验室捕获到MedusaLocker勒索病毒样本。该病毒从2019年10月份开始在国内传播，目前国内已有多家企业遭受此病毒攻击。Medusa
Ransom勒索病毒的名字起源于古希腊神话“美杜莎”，分析过程发现，该病毒的多个版本被泄露了出来，其中包括了黑客开发过程中的Debug版本。该病毒主要通过攻击者暴力破解远程桌面口令后手动运行感染，并且会遍历本地以及网络共享磁盘，使用RSA+AES方式加密数据文件，故在无相应私钥的情况下无法解密，危害性较高。

![4622f6b1831445e6b63aa6faf451b9ea](http://p1.pstatp.com/large/pgc-image/4622f6b1831445e6b63aa6faf451b9ea)

# 3 手工清除方法

结束名为svchostt.exe的进程，删除计划任务库根目录中名为“svchostt”的任务，删除本地svchostt.exe文件，删除6.3增加的注册表项。

# 4 应对措施及建议

面对恶意攻击我们除做好准备工作外，还需要及时采取高防措施，保护平台业务稳定发展不受影响。

1\. 安装江民杀毒软件病毒更新病毒库。

2\. 对不必要的机器关闭远程桌面服务。

3\. 对需要远程桌面服务的机器使用强密码，且两两不同。

4\. 病毒会排除对.rdp文件的加密，若中毒机器本地保存着对其他机器的rdp连接密码，则应对中毒的机器应立即隔离。

5\. 由于攻击者多为远程手动投毒，那么意味着即便安装了安全软件，攻击者也能手动结束安全软件，除非在安全软件上设定了更改验证密码。

6\. 禁用Guest账户。

7\. 检测系统和软件中的安全漏洞，及时更新补丁。

# 5 行为摘要

5.1 文件行为

创建C:\Users\Administrator\AppData\Roaming\svchostt.exe病毒文件

全盘遍历加密除指定后缀名之外的文件。

5.2 进程行为

创建“{8761ABBD-7F85-42EE-B272-A76179687C63}”互斥体

创建名为“svchostt”的计划任务

通过cmstplua COM接口提权

停止以下服务：wrapper,DefWatch,ccEvtMgr,ccSetMgr,SavRoam,sqlservr,sqlagent,sqladhlp,Culserver,RTVscan,sqlbrowser,SQLADHLP,QBIDPService,Intuit.QuickBooks.FCS,QBCFMonitorService,sqlwriter,msmdsrv,tomcat6,zhudongfangyu,SQLADHLP,vmware-usbarbitator64,vmware-converter,dbsrv12,dbeng8

重启以下服务以使得更改立即生效：

LanmanWorkstation

结束以下进程：

wxServer.exe,wxServerView,sqlservr.exe,sqlmangr.exe,RAgui.exe,supervise.exe,Culture.exe,RTVscan.exe,Defwatch.exe,sqlbrowser.exe,winword.exe,QBW32.exe,QBDBMgr.exe,qbupdate.exe,QBCFMonitorService.exe,axlbridge.exe,QBIDPService.exe,httpd.exe,fdlauncher.exe,MsDtSrvr.exe,tomcat6.exe,java.exe,360se.exe,360doctor.exe,wdswfsafe.exe,fdlauncher.exe,fdhost.exe,GDscan.exe,ZhuDongFangYu.exe

执行以下命令，删除系统备份，禁用系统恢复功能等：

vssadmin.exe Delete Shadows /All /Quiet

bcdedit.exe /set {default} recoveryenabled No

bcdedit.exe /set {default} bootstatuspolicy ignoreallfailures

wbadmin DELETE SYSTEMSTATEBACKUP

wbadmin DELETE SYSTEMSTATEBACKUP -deleteOldest

wmic.exe SHADOWCOPY /nointeractive

5.3 注册表行为

修改“HKLM\\\SOFTWARE\\\Microsoft\\\Windows\\\CurrentVersion\\\Policies\\\System”
下“EnableLUA”值为0（UAC窗口不再提示），
设置“ConsentPromptBehaviorAdmin”值为0（运行程序需要提权时不再需要输入凭证）

先修改“HKLM\\\SOFTWARE\\\Microsoft\\\Windows\\\CurrentVersion\\\Policies\\\System”下“EnableLinkedConnections”值为1（强制局域网共享的硬盘在本地创建符号链接，便于后续遍历加密）

创建HKCU\\\SOFTWARE\\\Medusa下“Name”值为“svchostt.exe”，为本程序名

5.4 网络行为

向本机地址发送ICMP包

# 6 详细分析报告

1\.
尝试打开名为"{8761ABBD-7F85-42EE-B272-A76179687C63}"的互斥体，若成功，代表已有勒索病毒运行，本进程退出；若无，本进程继续运行：

![85841959fcc9434f8f299abc832e4046](http://p1.pstatp.com/large/pgc-image/85841959fcc9434f8f299abc832e4046)

![799bbce283414f5bafdce54c1a2f7b5a](http://p1.pstatp.com/large/pgc-image/799bbce283414f5bafdce54c1a2f7b5a)

2\. 检测本进程是否具有管理员权限，若无，则通过cmstplua COM接口提权：

![8ab5f828a44d45d2876392b0451ff123](http://p1.pstatp.com/large/pgc-image/8ab5f828a44d45d2876392b0451ff123)

3\. 创建注册表项：

![811c84cc127e4a209bdb3214a005bbac](http://p1.pstatp.com/large/pgc-image/811c84cc127e4a209bdb3214a005bbac)

4\. 初始化加密相关函数，使用RSA+AES方式，得到本机识别id，创建勒索html文件，并填入本机识别id：

![8325347479bc4dc2ae79103730a78e8f](http://p3.pstatp.com/large/pgc-image/8325347479bc4dc2ae79103730a78e8f)

![e4d88e00d8f0415585b8866dc71373de](http://p3.pstatp.com/large/pgc-image/e4d88e00d8f0415585b8866dc71373de)

这也意味着被加密的文件在无私钥的情况下无法解密

5\. 创建病毒的持久化机制，即添加计划任务，这里通过CLSID_TaskScheduler COM接口添加，任务名为“svchostt”：

![eb1bc2d5cd994c42bab73565daec9fde](http://p9.pstatp.com/large/pgc-image/eb1bc2d5cd994c42bab73565daec9fde)

6\. 停止并删除指定服务，避免后续结束进程后进程重启，服务列表见进程行为部分：

![e4095a1fc38c4c17bd038c45581f321c](http://p1.pstatp.com/large/pgc-image/e4095a1fc38c4c17bd038c45581f321c)

7\. 终止指定进程，避免后续加密文件时进程占用，进程列表见进程行为部分：

![6ca85ff1b69d4cacad70b91d4aa8eab1](http://p1.pstatp.com/large/pgc-image/6ca85ff1b69d4cacad70b91d4aa8eab1)

8\. 终止本机的恢复机制等，包括清空回收站，删除系统备份等：

![110421c11f014e0a822721c0f6fedd4b](http://p3.pstatp.com/large/pgc-image/110421c11f014e0a822721c0f6fedd4b)

9\.
设置注册表"EnableLinkedConnections"值为1，后重启“LanmanWorkstation”服务，使得更改立即生效，该更改的效果为使得局域网共享磁盘在本地创建符号链接，使得后续遍历磁盘时能够遍历到，便于加密：

![68dbf8abeda14692854d389aec8567e1](http://p1.pstatp.com/large/pgc-image/68dbf8abeda14692854d389aec8567e1)

10\. 准备用于加密的目录，除了遍历得到目录外，还有预设尝试的重要目录：

![c753291c09374ba58f997c08614891fb](http://p9.pstatp.com/large/pgc-image/c753291c09374ba58f997c08614891fb)

11\. 开始加密：

![8ab6ca71e467400583f3bab15ece6b28](http://p1.pstatp.com/large/pgc-image/8ab6ca71e467400583f3bab15ece6b28)

加密会避过以下格式文件：

![e8e0***a0f69477baa762a210f622581](http://p1.pstatp.com/large/pgc-image/e8e0***a0f69477baa762a210f622581)

排除.encrypted以避免重复加密，另外，需要注意的是，作者避免了对.rdp格式文件的加密，这样就可以使得攻击者由保存的rdp密码继续攻击其他机器，务必注意！

# 7 附录(IOCs)

7.1 HASH

d54fa56f495571d8000ced3fefccf2a7

7.2 C&C

无

