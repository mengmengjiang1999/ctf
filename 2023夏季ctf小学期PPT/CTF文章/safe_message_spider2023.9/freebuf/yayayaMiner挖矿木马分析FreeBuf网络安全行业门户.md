## 1\. 活跃yayaya挖矿木马概览

近期，安天CERT捕获了一批活跃的挖矿木马样本，该挖矿木马主要利用SSH弱口令暴力破解对Linux平台进行攻击。由于其初始攻击脚本中多次出现“yayaya”字符串，且在Linux内核模块中会隐藏包含该字符串的所有信息，因此安天CERT将该挖矿木马命名为“yayaya
Miner”。

表 1‑1 活跃挖矿概览

 **活跃挖矿概览**

|

 **说明**  
  
---|---  
  
挖矿木马名称

|

yayaya Miner  
  
挖矿木马主要传播方式

|

利用SSH弱口令暴力破解  
  
出现时间

|

2022年11月底  
  
活跃时间

|

2023年4月活跃  
  
挖矿币种

|

门罗币  
  
针对系统

|

Linux  
  
主要技术特点

|

加密初始脚本；删除竞品挖矿；删除系统日志；使用开源工具隐藏内核模块等  
  
# 2\. 样本功能与技术梳理

yayaya
Miner挖矿木马使用shc工具加密初始攻击脚本，利用该工具可以把Shell脚本转换成二进制可执行文件（ELF），使用RC4加密算法对其进行加密，初始攻击脚本文件会删除系统日志、创建yayaya等目录、删除特定IP的网络连接、下载门罗币挖矿程序以及使用开源工具Diamorphine进行隐藏操作等。将其挖矿进程注入内存后进行隐藏，增加反病毒软件的检测难度。

### 2.1 yayayaxxxxxxxx（初始攻击脚本，X表示随机字符）

 **样本初始攻击脚本整体流程以及核心技术如下：**

  1. 初始文件实际为脚本文件，经过shc工具加密初始攻击脚本，可以把Shell脚本文件转换成二进制可执行文件（ELF）。该脚本首先会删除其他挖矿木马配置文件以及系统日志。
  2. 使用防火墙命令查找并删除其他挖矿木马挖矿所创建的网络连接，删除后下载自身zip (挖矿程序)。

  3. 使用开源工具 **Diamorphine** **对Linux** **内核模块和进程进行隐藏，** 具体为隐藏指定目录前缀“yayaya”，只要带有“yayaya”前缀的目录在系统中均不可见。将挖矿进程标记为隐藏，即在进程列表中不显示。指定内核模块名称为“nonono”。
  4. 将当前进程的用户和组ID都设置为0，以此实现获取root权限的功能。
  5. 编译内核模块ko并加载，使用kill命令向进程号为10000000的进程发送信号-63，触发模块的钩子函数。使用kill命令向指定进程发送信号-31，使其暂停执行。执行成功后删除/tmp/a目录中的所有文件及其子目录。

### 2.2 p.zip(挖矿程序)

p.zip压缩文件中包含一个名为“dsm_sa_ip”的文件，经判定，该文件为开源门罗币挖矿程序XMRig，采用加密通信的方式进行交互挖矿，矿池地址如下。

表 2‑1 矿池地址

 **矿池地址**

|

example.amax.fun:443

|

example.amax.fun:80

|

example.amax.fun:3333  
  
---|---|---|---  
  
example.gengzi.site:443

|

example.gengzi.site:80

|

example.gengzi.site:3333  
  
example.inspur.gay:443

|

example.inspur.gay:80

|

example.inspur.gay:3333  
  
example.sugon.store:443

|

example.sugon.store:80

|

example.sugon.store:3333  
  
dasan.one:443

|

dasan.one:80

|

dasan.one:3333  
  
172.104.170.240:443

|

172.104.170.240:80

|

172.104.170.240:3333  
  
# 3\. 挖矿木马落地排查与清除方案

### 3.1 yayaya Miner落地识别

1\. 文件（x表示随机字符）

 **文件名及路径：**

/usr/lib/x86_64-linux-gnu/yayayaxxxxxxxx

/etc/sysconfig/yayaya/dsm_sa_ip

2\. 网络侧排查

146.190.193.147:80（文件下载）

157.245.16.79:443（矿池连接）

3\. 服务执行路径

ExecStart=/usr/lib/x86_64-linux-gnu/yayayaxxxxxxxx

4\. 进程名称

八位随机字符串

5\. 内核模块名称

nonono  
  
---  
  
### 3.2 清除方案

1\. 将隐藏内核模块可见

kill -63 0

2\. 查看隐藏的内核模块nonono

cat /proc/modules |head -n 10

3\. 删除内核模块

rmmod nonono

4\. 结束挖矿进程

使用top命令查看最大占用系统资源的进程pid，使用命令kill -9
pid结束对于进程，该挖矿程序进程路径一般以类似的字符串形式存在“/112d9a3b”。

5\. 删除服务

rm -rf /usr/lib/systemd/system/yayayaxxxxxxxx.service

6\. 删除恶意文件

rm -rf /usr/lib/x86_64-linux-gnu/yayayaxxxxxxxx

rm -rf /etc/sysconfig/yayaya  
  
---  
  
# 4\. 防护建议

针对挖矿攻击安天建议企业采取如下防护措施：

  1. 安装终端防护：安装反病毒软件，针对不同平台安装相应的产品；
  2. 加强SSH口令强度：避免使用弱口令，建议使用16位或更长的口令，包括大小写字母、数字和符号在内的组合，同时避免多个服务器使用相同口令；
  3. 及时更新补丁：建议开启自动更新功能安装系统补丁，服务器应及时更新系统补丁；
  4. 及时更新第三方应用补丁：建议及时更新第三方应用如WebLogic等应用程序补丁；
  5. 开启日志：开启关键日志收集功能（安全日志、系统日志、错误日志、访问日志、传输日志和Cookie日志），为安全事件的追踪溯源提供基础；
  6. 主机加固：对系统进行渗透测试及安全加固；
  7. 部署入侵检测系统（IDS）：部署流量监控类软件或设备，便于对恶意代码的发现与追踪溯源。安天探海威胁检测系统（PTD）以网络流量为检测分析对象，能精准检测出已知海量恶意代码和网络攻击活动，有效发现网络可疑行为、资产和各类未知威胁；

![](https://image.3001.net/images/20230515/1684120830_6461a4feeaaf360a4823a.png!small)

图 4‑1 安天智甲可实现对该挖矿木马的有效查杀

# 5\. 事件对应的ATT&CK映射图谱

针对攻击者投放挖矿木马的完整过程，安天梳理本次攻击事件对应的ATT&CK映射图谱如下图所示。

![](https://image.3001.net/images/20230515/1684120815_6461a4efc1f131887e6ff.png!small)

图 5‑1 事件对应的ATT&CK映射图谱

攻击者使用的技术点如下表所示：

表 5‑1 事件对应的ATT&CK技术行为描述表

 **ATT &CK** **阶段** **/** **类别**

|

 **具体行为**

|

 **注释**  
  
---|---|---  
  
 **侦察**

|

主动扫描

|

扫描22端口  
  
 **初始访问**

|

利用外部远程服务

|

利用SSH远程服务访问  
  
 **执行**

|

利用命令和脚本解释器

|

使用Shell脚本  
  
 **持久化**

|

创建或修改系统进程

|

创建服务  
  
 **提权**

|

滥用提升控制权限机制

|

修改uid和gid提升权限  
  
 **防御规避**

|

使用Rootkit

|

使用LKM Rootkit  
  
隐藏行为

|

隐藏进程  
  
删除信标

|

删除恶意文件自身  
  
混淆文件或信息

|

使用shc工具混淆文件  
  
 **命令与控制**

|

使用加密信道

|

使用SSL加密信道  
  
 **影响**

|

资源劫持

|

占用CPU资源  
  
# 6\. IoCs

 **IoCs**  
  
---  
  
172.104.170.240  
  
example.amax.fun  
  
example.gengzi.site  
  
example.inspur.gay  
  
example.sugon.store  
  
dasan.one  
  
hxxp://example.established.site/p.zip  
  
hxxp://w.amax.fun/p.zip  
  
hxxp://172.104.170.240/p.zip  
  
# 参考资料

  * 典型挖矿家族系列分析二 | TeamTNT挖矿组织

https://www.antiy.cn/research/notice&report/research_report/20221207.html

  * Shc Linux Malware Installing CoinMiner

https://asec.ahnlab.com/en/45182/

