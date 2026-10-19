本报告由国家互联网应急中心（CNCERT）与安天科技集团股份有限公司（安天）共同发布。

##  **一** 、 **概述**

近期，CNCERT和安天联合监测发现Diicot挖矿组织（也称color1337、Mexals）频繁发起攻击活动，境内受害服务器已达600余台。

Diicot挖矿组织在此次活动中，以互联网下暴露22端口的设备作为攻击目标,使用SSH暴力破解工具实施入侵。成功后，根据设备CPU性能,利用托管网站下发不同载荷。当设备性能较弱时，从托管网站下载相应工具和脚本，实施扫描和暴力破解进行传播；当设备性能较强时，下载挖矿程序进行挖矿。

通过对攻击者使用的C2资源进行分析发现，攻击者于2022年10月13日至2023年5月27日期间不断更新攻击载荷，增加shc加密等手法以达成免杀的目的。跟踪监测发现2023年3月1日至今，境内受害服务器（以
IP 数计算）累计600余台。

 **表格1 Diicot组织挖矿活动概览**

**![1688091507_649e3b73b9e381fc48cf9.png!small](https://image.3001.net/images/20230630/1688091507_649e3b73b9e381fc48cf9.png!small)**

##  **二** 、 **攻击流程**

初始攻击程序Payload执行后，首先会清除主机中的全部定时任务，并结束竞品挖矿木马相关进程，根据受害者主机CPU核数的不同执行不同操作：

 **当核数少于4核时， Payload下载并运行History，用以启动传播程序Update，同时释放“protocols”。**
Update运行后会判断运行目录是否存在名为“Chrome”、“aliases”、“protocols”的文件，若不存在，则下载“Chrome”、“aliases”文件并运行。Chrome为Linux端口扫描器，运行后会扫描随机网段中开放22端口的设备，并将设备IP地址保存为“bios.txt”。aliases为SSH暴力破解工具，运行后使用“protocols”文件中保存的95组账号密码，对bios.txt中记录的IP地址，进行SSH暴力破解。若成功暴力破解某台设备，则会登录该设备并执行远程bash命令，用以结束竞品挖矿木马进程、下载并执行初始攻击程序payload。

**当核数大于或等于4核时，Payload会执行diicot，diicot为挖矿木马的启动程序，用于下载并运行挖矿程序Opera进行挖矿，Opera为开源挖矿组件xmrig。**
随后，diicot会清除主机中的全部定时任务，并结束竞品挖矿木马进程，创建名为“Example systemd
service”的服务和多个定时任务来实现挖矿程序Opera持久化运行。

 **图1 攻击流程图**

![1688091551_649e3b9fb4805921de339.png!small](https://image.3001.net/images/20230630/1688091551_649e3b9fb4805921de339.png!small)

##  **三** 、 **样本功能与技术梳理**

###  **3.1** **初始攻击程序Payload**

1、初始攻击程序Payload为SHC加密的BASH脚本，并使用修改后的UPX进行压缩保护，后续载荷均使用该方法进行压缩加密。

2、初始攻击程序Payload运行后会清除主机中的全部定时任务，并结束竞品挖矿木马相关进程。

3、根据受害者主机CPU核数的不同执行不同操作：当核数少于4核时，
Payload下载并运行传播启动程序History，用以启动传播程序Update，执行传播功能。

 **表格2 恶意程序下载地址和说明**

![1688091642_649e3bfa8f77663983a88.png!small](https://image.3001.net/images/20230630/1688091642_649e3bfa8f77663983a88.png!small)

当核数大于或等于4核时，执行挖矿启动程序diicot，用于下载并运行挖矿程序Opera，进行挖矿。

 **表格3 恶意程序下载地址和说明**

![1688091666_649e3c1247bbde29420fd.png!small](https://image.3001.net/images/20230630/1688091666_649e3c1247bbde29420fd.png!small)

4、Payload修改主机root账户密码，将新密码回传至攻击者服务器。

5、若CPU占用率超过50%，则会结束所有CPU占用率超过40%的进程。

6、攻击者将自定义的SSH密钥写入到主机中，用于SSH免密连接。

###  **3.2** **传播程序Update**

1、传播启动程序History运行后，执行传播程序Update。

2、Update运行会修改系统的打开文件数与用户进程数限制以保证后续代码的顺利执行，随后判断运行目录是否存在名为“Chrome”、“aliases”、“protocols”的文件，若不存在则下载并运行Linux端口扫描器Chrome和SSH暴力破解工具aliases。

 **表格4 恶意程序下载地址和说明**

![1688091695_649e3c2f226620d98431c.png!small](https://image.3001.net/images/20230630/1688091695_649e3c2f226620d98431c.png!small)

3、Update创建多个定时任务，实现持久化。

1）每天运行一次传播启动程序History

2）开机启动Update

3）每分钟、每月定时启动Update

![1688091817_649e3ca951a15cc51050f.png!small](https://image.3001.net/images/20230630/1688091817_649e3ca951a15cc51050f.png!small)

  

 **图2 Update创建多个定时任务**

4、执行Linux端口扫描器Chrome程序，扫描随机网段中开放22端口的设备，并将设备IP地址保存为“bios.txt”。

5、SSH暴力破解工具aliases运行后，使用“protocols”文件中保存的95组账号密码，对bios.txt中记录的IP地址，进行SSH暴力破解。其还具备信息回传、远程命令执行功能。aliases运行后向攻击者服务器回传目标主机地址、系统信息、用户名、登陆密码等数据。

6、若成功暴力破解某台设备，则会登录该设备执行远程bash命令，该命令用于清理结束竞品挖矿木马相关进程、下载并执行初始攻击程序。

7、在成功进行暴力破解后，回传受害者主机信息。其中，回传数据包括目标主机地址、系统信息、用户名、登陆密码等。

###  **3.3** **挖矿程序Opera**

挖矿启动程序diicot运行后创建“/var/tmp/.ladyg0g0/.pr1nc35”目录，并检查该目录中是否存在挖矿程序Opera和配置文件，若不存在则下载，该挖矿程序为开源挖矿组件xmrig。

 **表格5 恶意程序下载地址和说明**

![1688091941_649e3d2597acf91698990.jpg!small](https://image.3001.net/images/20230630/1688091941_649e3d2597acf91698990.jpg!small)

挖矿启动程序diicot会清除主机中的全部定时任务，并结束竞品相关进程，执行挖矿程序Opera。随后通过以下两种方式实现持久化：

1、创建名为“Example systemd service”的服务，每隔一小时检测一次Opera的运行状态，若停止运行则重新启动，保证挖矿程序的持续运行。

2、diicot创建多个定时任务，实现持久化。

1）每天运行一次挖矿启动程序diicot

2）开机启动挖矿启动程序diicot

3）每分钟、每月定时启动挖矿启动程序diicot

 **图3 diicot创建多个定时任务  
![1688091959_649e3d3789b7a52661c7b.png!small](https://image.3001.net/images/20230630/1688091959_649e3d3789b7a52661c7b.png!small)  
**

##  **四** 、 **挖矿木马落地排查与清除方案**

###  **4.1** **挖矿木马落地识别**

 **文件名：**

/var/tmp/Documents/.diicot

/var/tmp/Documents/Update

/var/tmp/Documents/History

/var/tmp/Documents/Opera

/var/tmp/Documents/config.json

/usr/bin/.locatione/

usr/bin/sshd

/var/tmp/Documents/aliases

/var/tmp/Documents/Chrome

/lib/systemd/system/myservice.service

/var/tmp/Documents/.5p4rk3l5

/var/tmp/.update-logs/.5p4rk3l5

 **网络侧排查**

arhivehaceru.com（攻击者服务器）

45.88.67.94（攻击者服务器）

45.88.67.94:7777（矿池）

139.99.123.196:80（矿池）

pool.supportxmr.com:80（矿池）

 **服务配置信息**

[Unit]

Description=Example systemd service.

[Service]

Type=simple

Restart=always

RestartSec=3600

ExecStart=/bin/bash /usr/bin/sshd

[Install]

WantedBy=multi-user.target

 **进程名称**

Opera

###  **4.2** **清除方案**

 **1** **、结束挖矿进程**

结束名为“Opera”且占用率高的进程

 **2** **、删除服务**

rm -rf /lib/systemd/system/myservice.service

 **3** **、删除定时任务**

rm -rf /var/tmp/Documents/.5p4rk3l5

rm -rf /var/tmp/.update-logs/.5p4rk3l5

 **4** **、删除恶意文件**

rm -rf /var/tmp/Documents/.diicot

rm -rf /var/tmp/Documents/Update

rm -rf /var/tmp/Documents/History

rm -rf /var/tmp/Documents/Opera

rm -rf /var/tmp/Documents/config.json

rm -rf /usr/bin/.locatione

rm -rf /usr/bin/sshd

rm -rf /var/tmp/Documents/aliases

rm -rf /var/tmp/Documents/Chrome

rm -rf /lib/systemd/system/myservice.service

rm -rf /var/tmp/Documents/.5p4rk3l5

rm -rf /var/tmp/.update-logs/.5p4rk3l5

##  **五、感染规模**

通过监测分析发现，国内于2023年3月1日至5月31日期间该挖矿木马日上线数最高达到200余台，累计已有600余台设备受其感染。每日境内上线数情况如下。

 **图4 每日上线境内数量**

**![1688092020_649e3d74d1f31d7746706.png!small](https://image.3001.net/images/20230630/1688092020_649e3d74d1f31d7746706.png!small)**

##  **六、防范建议**

请广大网民强化风险意识，加强安全防范，避免不必要的经济损失，主要建议包括：

1）加强口令强度，避免使用弱口令，密码设置要符合安全要求，并定期更换。建议使用16位或更长的密码，包括大小写字母、数字和符号在内的组合，同时避免多个服务器使用相同口令；

2）及时更新补丁，建议开启自动更新功能安装系统补丁，服务器应及时更新系统补丁；

3）及时更新第三方应用补丁，建议及时更新第三方应用如WebLogic等应用程序补丁；4）开启日志，开启关键日志收集功能（安全日志、系统日志、错误日志、访问日志、传输日志和Cookie日志），为安全事件的追踪溯源提供基础；

5）安装终端防护软件，定期进行全盘杀毒；

6）当发现主机感染挖矿程序后，立即核实主机受控情况和入侵途径，并对受害主机进行清理。

##  **七** 、 **相关IOC**

45.88.67.94

45.139.105.222

212.193.30.11

arhivehaceru.com

52CB6682849AE2978B6F07EC98DC550A

946689BA1B22D457BE06D95731FCBCAC

8CD22AE52EF7ADA0C6BDE9CBEDC992E1

0874C80875045B0F40B9D2A2FBAC1BBC

7B0DFEE24D9807D2ACA8FDC9E5E1AA0D

C9B7A680754497A2A681FA0F55636FEC

C689456EED1C848302797E3299CC8373

  

