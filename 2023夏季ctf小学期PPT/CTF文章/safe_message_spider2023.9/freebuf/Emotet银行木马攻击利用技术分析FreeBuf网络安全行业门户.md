## **概述** ****

Emotet是一种通过邮件传播的银行木马，诱骗用户点击执行恶意代码，最早被发现于2014年并持续活动至今，在国内也有一定的影响面，其积极的杀软对抗策略使之成为一个难缠的对手。

2019年9月23日奇安信病毒响应中心发布了Emotet威胁预警，经长期追踪，近期奇安信病毒响应中心发现多个带有恶意宏代码的Emotet鱼叉攻击邮件，邮件通过诱导用户点击启用宏从而执行宏代码，利用PowerShell下载并执行下阶段攻击载荷。具体攻击模块功能包括OutLook数据窃取以及横向渗透模块。

样本执行流程如下：

![图片.png](https://image.3001.net/images/20191108/1573208657_5dc5425139986.png!small)

## **样本分析** ****

###  **文档分析** ****

诱饵文档为英文编写，显示内容为提示用户启用宏：

![图片.png](https://image.3001.net/images/20191108/1573208753_5dc542b1bbc31.png!small)

当用户启用宏之后则会自动执行AutoOpen，从而触发宏代码。AutoOpen中最终会解码出一段Base64编码的PowerShell代码，随后调用PowerShelll执行该段Base64代码。

![图片.png](https://image.3001.net/images/20191108/1573208861_5dc5431d4df1f.png!small)  

Base64代码以及解码后数据如下：

![图片.png](https://image.3001.net/images/20191108/1573208869_5dc543250d7de.png!small)  

将解码的Base64数据整理之后发现该段代码会从五个不同的服务器中尝试下载下阶段攻击载荷，如果下载成功则执行该攻击载荷。

![图片.png](https://image.3001.net/images/20191108/1573208875_5dc5432bdb9f6.png!small)

此次使用的攻击载荷托管服务器有失陷主机，Emote也借此来躲避查杀。

### **Emotet** **Loader** **分析** ****

该样本参考编译时间为2019年10月7号，从奇安信病毒响应中心数据来看该PowerShell所访问的五个URL在国内的解析时间线几乎都是从10月26号开始![图片.png](https://image.3001.net/images/20191108/1573208886_5dc54336892d0.png!small)

该样本基于MFC编写，功能代码在导出函数中实现，在创建窗口之后通过消息处理函数来调用导出函数nZzNNxCMObNaV。

![图片.png](https://image.3001.net/images/20191108/1573208894_5dc5433e4664e.png!small)  

nZzNNxCMObNaV导出函数中调用的函数名称都是动态获取函数地址然后调用，函数名称通过资源ID来获取。

![图片.png](https://image.3001.net/images/20191108/1573208900_5dc543445ee84.png!small)  

随后使用RC 4解密ShellCode来执行，密钥为(vGdOmmadpKaisrM)：

![图片.png](https://image.3001.net/images/20191108/1573208908_5dc5434c31870.png!small)  

####  **Loader** **内加密ShellCode分析** ****

解密出的ShellCode中包含一个PE文件并在内存中加载，该DLL参考编译时间为10月18日：

![图片.png](https://image.3001.net/images/20191108/1573208915_5dc54353756d3.png!small)![图片.png](https://image.3001.net/images/20191108/1573208924_5dc5435c98497.png!small)  

在获取命令行参数之后会与“--b57a4fbf”进行比较，来判断是否有指定的参数存在，如果不存在则给定参数重新启动自身并退出当前进程：

![图片.png](https://image.3001.net/images/20191108/1573208931_5dc5436321243.png!small)  

带参启动之后获取磁盘序列号：

![图片.png](https://image.3001.net/images/20191108/1573208948_5dc5437417c64.png!small)  

格式化序列号作为Mutex的参数：

![图片.png](https://image.3001.net/images/20191108/1573208954_5dc5437acd56c.png!small)  

创建Mutex名称为"Global\I90D2908D"：

![图片.png](https://image.3001.net/images/20191108/1573208964_5dc5438452624.png!small)

以及Mutex: "Global\M90D2908D"：

![图片.png](https://image.3001.net/images/20191108/1573208970_5dc5438a1c0d2.png!small)

以及Mutex: "Global\E90D2908D"：

![图片.png](https://image.3001.net/images/20191108/1573208976_5dc543901f241.png!small)  

将自身文件Map到内存并计算CRC32的值：

![图片.png](https://image.3001.net/images/20191108/1573208983_5dc543976f5ee.png!small)  

获取计算机名称：

![图片.png](https://image.3001.net/images/20191108/1573208989_5dc5439d20a6b.png!small)  

创建名称为"sketchflow"的服务，并启动服务sketchflow.exe，该EXE为自身拷贝到system32目录下，随后该进程调用ExitProcess退出。

![图片.png](https://image.3001.net/images/20191108/1573208994_5dc543a2e8ebb.png!small)  

如果在创建服务器之前调用OpenSCManager失败则表示当前无法通过服务来保持自启动，则会通过Run注册表来保持持久性攻击的目的：

![图片.png](https://image.3001.net/images/20191108/1573209001_5dc543a91ef1d.png!small)  

调用系统API获取当前系统信息：

![图片.png](https://image.3001.net/images/20191108/1573209006_5dc543ae4e94a.png!small)  

通过PEB结构体获取当前进程SessionID：

![图片.png](https://image.3001.net/images/20191108/1573209016_5dc543b838259.png!small)  

枚举进程：

![图片.png](https://image.3001.net/images/20191108/1573209022_5dc543be36bf5.png!small)  

格式化出上线URL：

![图片.png](https://image.3001.net/images/20191108/1573209032_5dc543c8e07bc.png!small)  

调用Http系列函数与服务器通信：

![图片.png](https://image.3001.net/images/20191108/1573209042_5dc543d22b14c.png!small)  

如果通信成功则调用InternetReadFile从服务器读取数据，如果通信失败则通过通过WaitForSingleObject等待4571ms之后循环以上步骤。

![图片.png](https://image.3001.net/images/20191108/1573209048_5dc543d8f050b.png!small)![图片.png](https://image.3001.net/images/20191108/1573209056_5dc543e08812f.png!small)  

调用CryptDecrypt解密：

![图片.png](https://image.3001.net/images/20191108/1573209061_5dc543e54d4c8.png!small)

申请空间，修复导入表之后内存中创建线程加载从服务器下载的攻击载荷：

![图片.png](https://image.3001.net/images/20191108/1573209070_5dc543ee03541.png!small)

从服务器下载到数据之后处理分为三种方式：

![图片.png](https://image.3001.net/images/20191108/1573209087_5dc543ffcf058.png!small)

  

第一种直接将数据写入文件，并调用CreateProcess执行插件：

![图片.png](https://image.3001.net/images/20191108/1573209119_5dc5441fde456.png!small)

第二种是写入文件之后还可以在不同的Session下创建进程：

![图片.png](https://image.3001.net/images/20191108/1573209134_5dc5442e8fb49.png!small)

第三种是直接调用CreateThread来执行ShellCode：

![图片.png](https://image.3001.net/images/20191108/1573209139_5dc54433587c6.png!small)

奇安信病毒响应中心在对Emotet的持续关注中发现了另一个版本的Emotet Loader样本，在Emotet
Loader基本功能不变的情况下在对内加密ShellCode的处理上有了新的变化。

一种方法是通过将加密的ShellCode保存在数组中，另一种是将加密的ShellCode放置在资源数据中，通过FindResourceA等系列API获取资源并解密数据。

![图片.png](https://image.3001.net/images/20191108/1573209143_5dc54437e44bc.png!small)  

本次捕获的样本从服务器下载的PayLoad中实则还包含两个攻击模块。一个模块为窃取OutLook数据，另一个模块为横向渗透。

![图片.png](https://image.3001.net/images/20191108/1573209149_5dc5443db4225.png!small)

### **服务端请求的PayLoad分析** ****

通过创建线程的方法在内存在执行从服务器下载的PayLoad，该段代码Dump之后发现也是一个DLL，参考编译时间为2019年10月15日。

![图片.png](https://image.3001.net/images/20191108/1573209157_5dc544451fca9.png!small)  

执行DLLMain的代码，首先会尝试删除Temp目录下的文件，该文件由被注入到子进程创建，文件中保存的是获取的OutLook信息：

![图片.png](https://image.3001.net/images/20191108/1573209163_5dc5444b626ac.png!small)  

申请空间，在内存中释放准备注入到到进程的代码：

![图片.png](https://image.3001.net/images/20191108/1573209167_5dc5444fe9477.png!small)  

创建一个挂起的进程自身，参数为获取的OutLook数据保存的文件路径：

![图片.png](https://image.3001.net/images/20191108/1573209174_5dc5445687773.png!small)  

为子进程申请空间，调用GetThreadContext获取子进程的上下文信息，原本子进程的数据是映射在0x400000的位置：

![图片.png](https://image.3001.net/images/20191108/1573209180_5dc5445c8fe40.png!small)  

将之前在内存中释放的DLL写入到子进程中，并调用SetThreadContext设置子进程的EIP，从而执行注入的代码：

![图片.png](https://image.3001.net/images/20191108/1573209186_5dc544621ba31.png!small)

写入子进程的地址为0x40000，即子进程程序初始化时模块映射的地址，调用WriteProcessMemory写入该地址，覆盖原始数据，该注入技术为典型的Process
Hollowing。

![图片.png](https://image.3001.net/images/20191108/1573209191_5dc54467e50f0.png!small)  

子进程启动时由于被挂起，所以在线程恢复时执行RtlUserThreadStart，EAX的值指向线程执行的起始位置开始执行注入的DLL的OEP![图片.png](https://image.3001.net/images/20191108/1573209197_5dc5446d46e66.png!small)

随后等待进程执行完成退出，读取Temp文件的数据：

![图片.png](https://image.3001.net/images/20191108/1573209202_5dc54472df986.png!small)

连接服务器发送数据并等待数据返回：

![图片.png](https://image.3001.net/images/20191108/1573209208_5dc54478dcc1d.png!small)  

###  **注入到进程的模块1分析** ****

该模块为通过SetThreadContext注入到子进程中执行的DLL，参考编译时间为2019年3月31日。

![图片.png](https://image.3001.net/images/20191108/1573209217_5dc5448117c50.png!small)  

该DLL启动之后会查询OutLook的注册表DLLPathEx项的信息：

![图片.png](https://image.3001.net/images/20191108/1573209222_5dc5448621f25.png!small)![图片.png](https://image.3001.net/images/20191108/1573209226_5dc5448af04a9.png!small)  

在Temp目录下创建文件，该文件负责保存读取的OutLook的信息：

![图片.png](https://image.3001.net/images/20191108/1573209232_5dc544904d83c.png!small)  

该PayLoad会获取OutLook数据内容：

![图片.png](https://image.3001.net/images/20191108/1573209238_5dc54496cdee9.png!small)  

获取之后格式化，并将其写入到Tmp文件中，随后进程退出：

![图片.png](https://image.3001.net/images/20191108/1573209246_5dc5449ea237a.png!small)

  

### **模块** **2** **分析** ****

该模块通过线程直接在内存中执行。

模块启动之后会获取计算机名称以及当前进程名称，并在内存中解密出账号和密码的字典。

![图片.png](https://image.3001.net/images/20191108/1573209256_5dc544a842172.png!small)

解密出的密码字典如下：

![图片.png](https://image.3001.net/images/20191108/1573209261_5dc544ad91fdc.png!small)

枚举当前网络环境下的网络资源![图片.png](https://image.3001.net/images/20191108/1573209265_5dc544b11a93f.png!small)

尝试使用字典连接到目标服务器，如果成功则拷贝自身文件到目标机器，并通过服务器启动进程已达到横向渗透的目的：

![图片.png](https://image.3001.net/images/20191108/1573209271_5dc544b7ce7a3.png!small)

## **小结** ****

奇安信病毒响应中心发现多个同源样本，样本中使用的Loader以及从服务器下载的PayLoad均有所差异，不排除Emotet背后的攻击者在改进样本功能的同时也在规避杀软对相似样本的同源查杀。从样本行为来看此次攻击活动主要目的是获取用户计算机信息以，OutLook数据以及做横向渗透，攻击者可能在为后续深入攻击做铺垫。

奇安信病毒响应中心提醒用户不要轻易打开未知邮件，提高安全意识。预防此类恶意样本攻击。

目前奇安信集团全线产品，包括天擎、天眼、SOC、态势感知、威胁情报平台，支持对涉及该报告相关的攻击活动检测。

## **IOCs** ****

hxxp://[www.encitmgdk.com/wp-content/jz9j7hptcw-bgwvnoaacn-64826306/](http://www.encitmgdk.com/wp-content/jz9j7hptcw-bgwvnoaacn-64826306/)

hxxp://new.1communityre.com/wp-admin/NhwvCC/

hxxps://simplecuisine.000webhostapp.com/wp-admin/UOdPpFk/

hxxps://ejerciciosantonio.000webhostapp.com/wp-admin/yds9q9bnpj-gp81uc99l-661630/

hxxps://edu.tizino.com/wvcly/uvsMEaKW/

96.20.84.254

45.56.122.75

85.25.92.96

94.177.253.126

189.166.13.109

212.112.113.235

216.70.88.55

138.186.179.235

95.216.207.86

176.58.93.123

189.132.130.111

75.154.163.1

60.52.64.122

181.36.42.205

143.95.101.72

203.99.188.11

70.45.30.28

110.36.234.146

190.117.206.153

190.55.39.215

186.84.173.153

187.143.219.242

181.47.235.26

185.45.24.254

190.13.146.47

5.189.148.98

190.217.1.149

200.55.168.82

154.120.227.206

162.241.134.130

190.228.212.165

91.109.5.28

190.96.118.15

70.32.94.58

83.169.33.157

190.113.146.128

144.76.62.10

201.217.113.58

216.75.37.196

181.61.143.177

211.229.116.130

157.7.164.178

186.92.11.143

203.99.187.137

187.188.166.192

203.99.188.203

190.16.101.10

201.196.15.79

113.52.135.33

186.109.91.136

189.218.243.150

42.190.4.92

178.249.187.150

138.197.140.163

51.38.134.203

23.253.207.142

186.146.110.108

152.170.220.95

200.90.86.170

192.241.220.183

172.104.70.207

181.197.2.80

<http://111.119.233.65/codec/site/>

<http://190.210.184.138/ban/>

<http://51.255.165.160/loadan/enabled/raster/merge/>

<http://45.56.79.249/arizona/>

<http://163.172.40.218/health/>

<http://91.205.215.57/stubs/symbols/raster/merge/>

<http://68.183.170.114/iab/arizona/raster/merge/>

<http://190.217.1.149/site/add/>

<http://62.75.160.178/child/sess/>

<http://200.113.106.18/publish/iab/raster/>

<http://5.196.35.138/devices/prov/raster/>

<http://89.188.124.145/prep/devices/raster/>

<http://89.188.124.145/vermont/srvc/>

<http://186.23.132.93/entries/ban/scripts/merge/>

<http://51.15.8.192/loadan/sym/>

<http://190.38.14.52/usbccid/cone/scripts/merge/>

<http://217.199.160.224/usbccid/>

<http://207.154.204.40/report/xian/scripts/>

<http://142.93.114.137/health/prep/>

<http://94.183.71.206/iplk/>

<http://190.104.253.234/pnp/balloon/scripts/>

<http://212.71.237.140/bml/teapot/scripts/>

<http://201.163.74.202/publish/scripts/scripts/merge/>

<http://201.190.133.235/bml/usbccid/>

<http://186.15.57.7/scripts/child/>

<http://86.42.166.147/acquire/>

<http://82.196.15.205/cookies/>

<http://186.68.141.218/taskbar/ringin/>

<http://46.28.111.142/scripts/>

<http://138.68.106.4/health/cookies/scripts/merge/>

<http://190.10.194.42/child/codec/scripts/merge/>

<http://104.131.58.132/guids/ban/scripts/merge/>

<http://104.131.58.132/guids/ban/scripts/merge/>

<http://190.230.60.129/badge/entries/>

<http://109.169.86.13/guids/>

<http://181.44.166.242/merge/tlb/scripts/>

<http://46.41.151.103/sess/xian/scripts/>

<http://144.139.158.155/devices/sess/scripts/>

<http://183.82.97.25/psec/chunk/scripts/merge/>

<http://149.62.173.247/raster/devices/scripts/>

<http://81.169.140.14/xian/splash/>

<http://190.230.60.129/enable/acquire/scripts/merge/>

<http://190.230.60.129/enable/acquire/scripts/merge/>

<http://77.245.101.134/child/between/scripts/merge/>

<http://46.29.183.211/acquire/>

<http://68.183.190.199/balloon/>

<http://220.241.38.226/guids/arizona/scripts/>

<http://45.79.95.107/attrib/xian/>

<http://200.58.83.179/balloon/srvc/>

<http://190.97.30.167/schema/vermont/scripts/>

<http://178.79.163.131/symbols/devices/scripts/merge/>

<http://77.55.211.77/badge/splash/scripts/merge/>

<http://201.213.32.59/site/acquire/scripts/merge/>

<http://79.143.182.254/teapot/>

<http://14.160.93.230/stubs/entries/scripts/>

<http://178.249.187.151/entries/report/scripts/>

<http://190.182.161.7/pdf/arizona/>

<http://181.59.253.20/ringin/jit/scripts/merge/>

<http://139.5.237.27/results/ringin/scripts/>

<http://154.120.227.206/ringin/iab/scripts/>

<http://91.83.93.124/chunk/vermont/>

<http://181.16.17.210/stubs/cookies/>

<http://80.85.87.122/jit/balloon/scripts/merge/>

<http://119.59.124.163/badge/tpt/>

<http://190.230.60.129/site/raster/scripts/>

<http://181.135.153.203/cab/enabled/scripts/>

<http://185.86.148.222/usbccid/entries/>

<http://46.101.212.195/devices/taskbar/scripts/merge/>

<http://200.113.106.18/usbccid/symbols/scripts/>

<http://50.28.51.143/splash/>

<http://86.6.188.121/report/chunk/>

<http://62.75.143.100/between/prov/scripts/merge/>

<http://81.213.215.216/guids/iplk/>

<http://181.36.42.205/acquire/>

<http://186.1.41.111/attrib/>

<http://203.25.159.3/sess/>

<http://79.127.57.43/jit/window/>

<http://69.163.33.84/vermont/bml/scripts/merge/>

<http://190.146.131.105/prep/>

<http://87.106.77.40/symbols/>

<http://91.204.163.19/walk/ringin/scripts/>

<http://94.177.183.28/codec/publish/>

<http://111.119.233.65/enabled/>

<http://190.210.184.138/enabled/iplk/scripts/merge/>

<http://51.255.165.160/forced/>

<http://45.56.79.249/badge/site/>

<http://163.172.40.218/arizona/walk/scripts/>

<http://68.183.170.114/badge/merge/scripts/>

<http://68.183.170.114/badge/merge/scripts/>

<http://62.75.160.178/usbccid/taskbar/>

<http://200.113.106.18/json/forced/scripts/>

<http://89.188.124.145/sym/img/scripts/>

<http://186.23.132.93/badge/prep/scripts/merge/>

<http://51.15.8.192/ringin/vermont/scripts/merge/>

<http://190.38.14.52/json/devices/scripts/merge/>

<http://217.199.160.224/cookies/splash/scripts/merge/>

<http://207.154.204.40/attrib/json/raster/>

<http://207.154.204.40/attrib/json/raster/>

<http://94.183.71.206/glitch/enabled/raster/>

<http://212.71.237.140/between/taskbar/raster/merge/>

<http://201.163.74.202/loadan/loadan/>

<http://201.190.133.235/odbc/img/>

<http://186.15.57.7/cab/srvc/raster/>

<http://86.42.166.147/scripts/attrib/>

<http://82.196.15.205/report/devices/>

<http://186.68.141.218/attrib/tpt/raster/>

<http://46.28.111.142/attrib/json/>

<http://138.68.106.4/forced/window/raster/>

<http://190.10.194.42/splash/>

<http://104.131.58.132/schema/cone/raster/>

<http://190.96.118.15/health/report/raster/>

<http://190.230.60.129/loadan/xian/>

<http://109.169.86.13/cone/>

<http://181.44.166.242/enabled/chunk/raster/>

<http://46.41.151.103/schema/iplk/>

<http://144.139.158.155/sym/badge/raster/>

<http://183.82.97.25/jit/>

<http://149.62.173.247/health/pnp/>

<http://81.169.140.14/loadan/enabled/raster/>

<http://190.230.60.129/symbols/>

<http://159.203.204.126/acquire/child/raster/>

<http://77.245.101.134/publish/symbols/raster/merge/>

<http://46.29.183.211/balloon/pdf/raster/merge/>

<http://68.183.190.199/json/chunk/raster/>

<http://220.241.38.226/jit/vermont/>

<http://45.79.95.107/chunk/devices/>

<http://190.97.30.167/srvc/health/raster/merge/>

<http://178.79.163.131/results/walk/raster/>

<http://190.120.104.21/acquire/raster/>

<http://77.55.211.77/iplk/enabled/>

<http://201.213.32.59/health/between/raster/merge/>

<http://79.143.182.254/report/cone/raster/merge/>

<http://14.160.93.230/schema/arizona/raster/>

<http://178.249.187.151/child/xian/>

<http://190.182.161.7/between/>

<http://181.59.253.20/srvc/prov/raster/merge/>

<http://139.5.237.27/scripts/cookies/raster/>

<http://154.120.227.206/codec/balloon/raster/>

<http://91.83.93.124/cookies/splash/>

<http://181.16.17.210/enable/json/raster/merge/>

<http://80.85.87.122/rtm/>

<http://119.59.124.163/ringin/usbccid/>

<http://190.230.60.129/iplk/>

<http://181.135.153.203/loadan/>

<http://185.86.148.222/loadan/tlb/raster/>"

<http://46.101.212.195/prov/>

<http://200.113.106.18/window/>

<http://201.184.41.228/stubs/enable/>

<http://50.28.51.143/window/>

<http://86.6.188.121/arizona/balloon/raster/merge/>

<http://62.75.143.100/prep/tpt/raster/>

<http://81.213.215.216/loadan/json/>

<http://181.36.42.205/entries/>

<http://186.1.41.111/enable/glitch/raster/merge/>

<http://203.25.159.3/cab/>

<http://79.127.57.43/loadan/forced/raster/>

<http://69.163.33.84/raster/pdf/raster/>

<http://41.75.135.93/tlb/nsip/>

<http://190.146.131.105/arizona/publish/raster/merge/>

<http://87.106.77.40/raster/vermont/raster/merge/>

<http://91.204.163.19/prep/iplk/raster/merge/>

<http://94.177.183.28/vermont/odbc/>

<http://51.254.218.210/iab/attrib/acquire/merge/>

"

MD5:

ac43864554afc20fa59f566478ccbc40

9b5420158051489fac6c1cc39da24d0e

a5f72b5208932166da5de59fb4f8d677

36299b628141fe5180de72fd2e3a2d7c

8B9F1CFED7737B18D12852437FC931EE

5C5471FF7249E476139E1FE3646A12D5

5910AD3C0E94711173A03FD65A2930B5

baa9c43bb34d3fe2212a6a023a50dc1e

参考链接：

[
_https://mp.weixin.qq.com/s/61Mq92hOmcaKoxKUBJhfAA_](https://www.freebuf.com/column/215015.html)

