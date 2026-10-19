## 用户可能会问的问题

感染勒索病毒的用户最关注的往往就两点，我的业务什么时候能恢复上线，我的数据还能不能找回来？

1、我要尽快恢复业务，大领一直在问什么时候可以恢复？【最关注】

恢复业务的时间取决于何时能确认本次勒索病毒的感染范围、传播途径、抑制措施的落地，最重要的是您这边的数据是否有备份。

2、我没有可用的数据备份，这些数据还能恢复嘛？【最关注】

如果没有数据备份的话，需要根据勒索病毒的家族和版本情况判断是否能解密，目前大部分勒索病毒都无法破解。

因为勒索病毒加密的文件必须通过黑客手里的私钥去解密，私钥没有公开或当前病毒程序没有BUG的情况下基本无法破解。

3、我有备份，下一步我应该怎么做？

可以先重装系统并导入备份数据，但需要等勒索病毒抑制措施落地后才能将系统上线。

4、以后还会不会再中招？这次是因为什么原因造成的？

根据溯源结果回答，做好对应的防御措施可一定程度抵挡病毒再次入侵，但安全不是绝对的。这次是因为xxx原因直接导致服务器失陷并且因为xxx原因导致内网横向感染爆发。

1、内部3389端口滥用——缺乏堡垒机运维和安全运维

2、windows系统不打补丁，445端口开放——缺乏主机漏洞管理，缺乏终端防护

3、外网WEB系统高危漏洞——缺乏漏扫和渗透测试

4、内网服务器管理后台类端口映射出公网——运维不规范

5、我买了你们家这么多设备，为什么还会中招呢？（一些比较强硬的用户焦虑急于甩锅）

安全不是绝对的，安全设备再好再多也需要配置符合您这边环境的策略，同时也需要专业的技术人员去分析运维和优化。

6、我这还有几台Linux服务器，会不会也中病毒啊？要不要也断网？

用户问这个问题的本质是不清楚本次勒索病毒的行为特征，首先要确认的是Linux服务器也会中勒索，但这次的病毒不一定有感染Linux服务器的代码，但由于本次感染范围较大，且具体情况不明了，如果这台服务器与感染网段网络互通，最好先下线后等安全后再上线。

## 现场需要哪些协助

1、需要有客户对接人协调相关人员例如服务器登录账号密码和相关安全设备登录密码

2、网络端口策略封堵需要网络对接人执行（交换机/防火墙）

3、需要销售在现场一起做最终汇报

# 如何改善这些问题

提前思考用户可能会问的问题并想好该如何回答让客户信任你

提前确定好进场后要做的事情以及需要协助的点，立即联系用户对接人并将以下文字及时同步至群聊（语音沟通的可能会漏），让用户侧提供并执行以下操作：

1、立即对已知感染机器断网，未感染机器若未安装杀软也需要断网，即使安装杀软也建议断网等服务器区域确认安全后再上线。【尽量不要关机重启，物理机拔网线虚拟机禁用网卡】  
2、勒索病毒加密文件后缀、勒索信息截图，用户发现这个问题的时间点确认（现场人员拍照截图同步）  
3、感染机器信息统计——系统名称、IP地址（确认本次影响范围）  
4、感染机器所在网络拓扑（越全越好）、外网出口映射表（出口防火墙）  
5、立即对137-139，445，3389端口策略封堵（内网病毒传播一般都是这几个端口），网络层和终端层都需要做（交换机ACl/EDR微隔离策略）  
6、未感染服务器需要安装部署EDR并开启端口隔离和全盘杀毒，杀完毒后可临时上线满足业务。

## 过程中汇报处置进度如（根据处置进度不断更新内容）：

不断在群里更新处置进度会让客户感知到我们的努力，很多时候用户不是很懂技术，应急响应报告也不一定会看，如果缺乏互动和沟通会极大影响客户情绪，几句话概括的处置进度往往可以让客户大概知道我们在干什么也知道需要他来干什么，增加互动感。

### 今日处置模版:

（1）将所有感染服务器和未感染服务器但与感染服务器网络互通均执行断网操作——已完成  
（2）确认本次勒索病毒家族为XXX，最早加密文件时间为xxx——已完成  
（3）确认感染机器信息统计-系统名称、IP地址-输出统计表——已完成  
（4）内网服务器区域防火墙（若有）下发3389,445端口的禁止策略（双向）————已完成  
（5）在服务器区域进行了下全网段的3389与445端口扫描，梳理出开放的端口主机列表，然后逐个的进 行EDR部署和端口封禁；——已完成  
对未感染服务器部署EDR并开启端口隔离和全盘杀毒，杀完毒后可临时上线满足业务。——已完成  
对已感染服务器进行逐个溯源，根据加密文件时间（everything）找到最早被感染的主机是xxx，再根据主机痕迹和安全设备日志关联溯源出攻击路径和入侵源是xxx——已完成  
完成溯源后，已感染服务器需重装系统。  
（6）修改本次影响网段内所有服务器的登录账号密码，密码需满足一定强度和复杂度并且不具有通用性。  
后续工作内容模版  
（7）完成服务器加固后，需要对终端PC进行杀软查杀和端口封堵——待执行  
（8）后续建议开启堡垒机替代3389远程桌面运维，仅允许堡垒机访问服务器区域的远程桌面端口（避免病毒RDP爆破感染）——待执行  
（9）xxx服务器异常外联问题——待执行

（10）xxx安全设备存在策略不合规，需调整为xxx

（11）漏扫发现服务器存在大量高危漏洞，建议及时进行修复防止被恶意利用。（修复漏洞需提前备份数据进行测试）——待执行

# 一些不太重要的技术分享

### 信息收集

1\. 收集客户网络拓扑便于尽快熟悉现场网络环境，并确认风险区域

2\. 收集客户外网映射（出口防火墙）以便关联判断溯源

3\. 收集加密文件后缀和勒索邮件以便确认勒索病毒家族

4\. 已感染服务器和未感染但处于风险区域的服务器IP、系统信息统计

输出统计表

## 应急处置

1\. 感染服务器立即断网（不关机或重启）

2\. 未感染但处于风险网段的服务器也建议断网，如无法断网，需要判断勒索病毒传播途径后立即封堵对应端口，一般均通过445，3389端口传播

有的时候开启服务器本地防火墙会导致客户业务无法使用，这种情况下需要梳理出客户业务所需端口，定制化开启防火墙策略。或者安装EDR开启端口微隔离，不影响原有业务端口

  * 批处理脚本一键封堵445,3389出入站

echo off

netsh advfirewall set allprofiles state on

netsh advfirewall firewall add rule name="DenyRiskPortIn" dir=in action=Block
protocol=TCP localport=135-139,445,3389 enable=yes

netsh advfirewall firewall add rule name="DenyRiskPortOut" dir=out
action=Block protocol=TCP localport=135-139,445,3389 enable=yes

puase

![1648783545_624670b90062a362cb184.png!small?1648783545096](https://image.3001.net/images/20220401/1648783545_624670b90062a362cb184.png!small?1648783545096)

![1648783553_624670c1322676e2b6741.png!small?1648783553468](https://image.3001.net/images/20220401/1648783553_624670c1322676e2b6741.png!small?1648783553468)

## 溯源分析

### 1\. 远程连接注意事项

  * 关闭本地磁盘映射(默认关闭，防止磁盘被挂载后也被勒索病毒加密)![1648783570_624670d257b024a6c8a93.png!small?1648783570802](https://image.3001.net/images/20220401/1648783570_624670d257b024a6c8a93.png!small?1648783570802)

### 2\. 主机信息取证

使用批处理一键收集主机上关键信息，基于大佬写的改了点东西。可以收集当前网络连接、进程信息、启动项、计划任务、所有系统日志文件等

![1648783577_624670d950be822d193df.png!small?1648783577696](https://image.3001.net/images/20220401/1648783577_624670d950be822d193df.png!small?1648783577696)![1648783583_624670dfa972bfea3ab22.png!small?1648783584313](https://image.3001.net/images/20220401/1648783583_624670dfa972bfea3ab22.png!small?1648783584313)

### 3\. 根据加密文件时间找进程（需要在感染服务器上操作）

使用everything找到最早的加密文件时间，文件加密是一个个加密的，所以存在时间差异，配合系统日志关联分析，找到最早被加密的服务器

将txt修改为加密文件后缀如eking,可以找到最早被加密文件的时间

![1648783591_624670e7a0678df3b85d3.png!small?1648783591838](https://image.3001.net/images/20220401/1648783591_624670e7a0678df3b85d3.png!small?1648783591838)

根据以上时间段找关联的exe文件，dm指文件修改时间

![1648783600_624670f05bb2fad11b98b.png!small?1648783600434](https://image.3001.net/images/20220401/1648783600_624670f05bb2fad11b98b.png!small?1648783600434)

同时也可根据上面批处理脚本获得recentrunprocess.txt排查指定时间段内服务器运行了哪些进程（实测server2008r2无Prefetch，win7有）

![1648783609_624670f94d2cd4e753d24.png!small?1648783610159](https://image.3001.net/images/20220401/1648783609_624670f94d2cd4e753d24.png!small?1648783610159)

使用Process Explorer开启starttime列找恶意进程时间

![1648783624_62467108ae146bf7571cc.png!small?1648783626651](https://image.3001.net/images/20220401/1648783624_62467108ae146bf7571cc.png!small?1648783626651)

![1648783632_62467110c683f3d4ba3ab.png!small?1648783633067](https://image.3001.net/images/20220401/1648783632_62467110c683f3d4ba3ab.png!small?1648783633067)

### 4\. 根据网络连接行为和PID找进程

一般此类行为是病毒的传播程序，在尝试对其他主机进行445端口扫描和漏洞利用

![1648783640_624671182d0d10e3d13bf.png!small?1648783640473](https://image.3001.net/images/20220401/1648783640_624671182d0d10e3d13bf.png!small?1648783640473)

![1648783648_624671203636d688f5c3f.png!small?1648783649449](https://image.3001.net/images/20220401/1648783648_624671203636d688f5c3f.png!small?1648783649449)

PE也可以看到该进程绑定的服务是mssecsvc.2.0,kill掉这个进程后还需要删除此服务才可清除，否则依然会再次启动

![1648783656_6246712864b5f845eaf9e.png!small?1648783656673](https://image.3001.net/images/20220401/1648783656_6246712864b5f845eaf9e.png!small?1648783656673)

![1648783662_6246712e9cac9c8b81073.png!small?1648783662650](https://image.3001.net/images/20220401/1648783662_6246712e9cac9c8b81073.png!small?1648783662650)

### 5\. 驻留程序分析

恶意程序常见的驻留程序如下,找到恶意进程后再去找驻留程序（内容有点多，回头单独整理一下）

  * 开机启动项
  * 服务
  * Dll注入svchost等
  * WMI无文件

### 6\. 服务器系统日志分析

  * 重点分析哪几个日志文件，使用什么工具

重点查看以下3个日志文件，使用Logparser工具（微软官方）直接看事件查看器点的实在太累了。

![1648783681_624671410bc55768a4f85.png!small?1648783681467](https://image.3001.net/images/20220401/1648783681_624671410bc55768a4f85.png!small?1648783681467)

Microsoft-Windows-TerminalServices-RDPClient%4Operational是本机访问其他机器的日志，可用于判断主机是否攻陷其他机器

Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational是其他机器成功登录本机的日志

Security保存的日志类型较多，主要关注以下事件ID：

4624 表示登录成功

4625表示登录失败

1102表示日志清除

4720表示新用户创建

使用实例：

在收集的日志路径下进入cmd（需要管理员权限运行）

![1648783710_6246715ea643e05b20cd6.png!small?1648783711323](https://image.3001.net/images/20220401/1648783710_6246715ea643e05b20cd6.png!small?1648783711323)

1、登录成功且登录类型为10（RDP）的事件

LogParser.exe -i:EVT -o:DATAGRID "SELECT
TimeGenerated,EXTRACT_TOKEN(Strings,8,'|')as
LoginType,EXTRACT_TOKEN(Strings,18,'|')as
LoginIP,EXTRACT_TOKEN(Strings,5,'|')as Username FROM Security.evtx where
EventID=4624 and EXTRACT_TOKEN(Strings,8,'|')='10'"

![1648783717_62467165b034aedbcf39a.png!small?1648783717878](https://image.3001.net/images/20220401/1648783717_62467165b034aedbcf39a.png!small?1648783717878)

2、登录成功且登录类型为3（SMB）的事件

LogParser.exe -i:EVT -o:DATAGRID "SELECT
TimeGenerated,EXTRACT_TOKEN(Strings,8,'|')as
LoginType,EXTRACT_TOKEN(Strings,18,'|')as
LoginIP,EXTRACT_TOKEN(Strings,5,'|')as Username FROM Security.evtx where
EventID=4624 and EXTRACT_TOKEN(Strings,8,'|')='3'"

![1648783723_6246716b5dbc43fce5891.png!small?1648783723431](https://image.3001.net/images/20220401/1648783723_6246716b5dbc43fce5891.png!small?1648783723431)

3、登录失败且登录类型为10（RDP）的事件——RDP爆破

LogParser.exe -i:EVT -o:DATAGRID "SELECT
TimeGenerated,EXTRACT_TOKEN(Strings,10,'|')as
LoginType,EXTRACT_TOKEN(Strings,19,'|')as
LoginIP,EXTRACT_TOKEN(Strings,5,'|')as Username FROM Security.evtx where
EventID=4625 and EXTRACT_TOKEN(Strings,10,'|')='10'"

![1648783729_624671716e1f4506d9c6e.png!small?1648783729432](https://image.3001.net/images/20220401/1648783729_624671716e1f4506d9c6e.png!small?1648783729432)

4、登录失败且登录类型为3（SMB）的事件——SMB爆破

LogParser.exe -i:EVT -o:DATAGRID "SELECT
TimeGenerated,EXTRACT_TOKEN(Strings,10,'|')as
LoginType,EXTRACT_TOKEN(Strings,19,'|')as
LoginIP,EXTRACT_TOKEN(Strings,5,'|')as Username FROM Security.evtx where
EventID=4625 and EXTRACT_TOKEN(Strings,10,'|')='3'"

![1648783735_6246717787fe2a0e4929c.png!small?1648783735762](https://image.3001.net/images/20220401/1648783735_6246717787fe2a0e4929c.png!small?1648783735762)

5、指定登录时间范围的事件

在确定主机失陷时间后，查看一下失陷时间左右的所有日志，检查是否有用户创建等其他异常事件

LogParser.exe -i:EVT -o:DATAGRID "SELECT * FROM Security.evtx where
TimeGenerated>'2018-06-19 23:32:11' and TimeGenerated<'2018-06-20 23:34:00'"

6、提取登录成功的用户名和IP(部分爆破日志无源地址看第七条)

LogParser.exe -i:EVT -o:DATAGRID "SELECT EXTRACT_TOKEN(Message,13,' ') as
EventType,TimeGenerated as LoginTime,EXTRACT_TOKEN(Strings,5,'|') as
Username,EXTRACT_TOKEN(Message,38,' ') as Loginip FROM Security.evtx where
EventID=4624"

![1648783746_624671826a249fb2d4349.png!small?1648783746591](https://image.3001.net/images/20220401/1648783746_624671826a249fb2d4349.png!small?1648783746591)

7、提取登录成功的IP(可以直接看到登录源地址)

LogParser.exe -i:EVT -o:DATAGRID "SELECT
TimeGenerated,EventID,EXTRACT_TOKEN(Strings,2,'|') as LoginIP FROM Microsoft-Windows-TerminalServices-RemoteConnectionManager%4Operational.evtx where
EventID=1149"

![1648783752_624671887a2cc0b0d7147.png!small?1648783752619](https://image.3001.net/images/20220401/1648783752_624671887a2cc0b0d7147.png!small?1648783752619)

  * 溯源发现攻击源是0.0.1是什么情况

某些情况下看日志发现攻击源地址是本机地址，此时可能是因为攻击者在服务器上传了frp之类的反向代理软件将rdp端口代理出外网并利用mimikaz获取密码或者RDP爆破最终登录该主机远程桌面。

在frp服务端配置如下：

![1648783762_6246719245b20bdef6fa9.png!small?1648783762293](https://image.3001.net/images/20220401/1648783762_6246719245b20bdef6fa9.png!small?1648783762293)

在失陷服务器配置如下（一般黑客通过web漏洞攻陷主机上传此类代理软件）：

![1648783768_6246719811444df0f14e1.png!small?1648783768206](https://image.3001.net/images/20220401/1648783768_6246719811444df0f14e1.png!small?1648783768206)

配置后直接访问FRP服务端所在公网服务器的33312端口即访问失陷主机的3389远程桌面

![1648783775_6246719f60a71d4f54d51.png!small?1648783775453](https://image.3001.net/images/20220401/1648783775_6246719f60a71d4f54d51.png!small?1648783775453)

无论是安全日志还是RDP操作日志都未记录攻击源地址，只有本机127.0.0.1地址

![1648783783_624671a74466f8a71c4a9.png!small?1648783783318](https://image.3001.net/images/20220401/1648783783_624671a74466f8a71c4a9.png!small?1648783783318)

![1648783787_624671ab843cd1ee0c39e.png!small?1648783787736](https://image.3001.net/images/20220401/1648783787_624671ab843cd1ee0c39e.png!small?1648783787736)

网络连接中可以看到失陷主机与frp服务端已建立连接，可以根据此连接找到对应进程文件。

![1648783825_624671d1619475de01c04.png!small?1648783825486](https://image.3001.net/images/20220401/1648783825_624671d1619475de01c04.png!small?1648783825486)

![1648783838_624671deb1cec6fb72dac.png!small?1648783839111](https://image.3001.net/images/20220401/1648783838_624671deb1cec6fb72dac.png!small?1648783839111)

当黑客正在连接此服务器时，服务器本机会创建两个127.0.0.1本地连接用户RDP会话，并将RDP流量通过frp传输至FRP服务端。

![1648783856_624671f0cf6cbf508e496.png!small?1648783857102](https://image.3001.net/images/20220401/1648783856_624671f0cf6cbf508e496.png!small?1648783857102)

  * 主机杀软日志![1648783866_624671fad8003e0cf8309.png!small?1648783868511](https://image.3001.net/images/20220401/1648783866_624671fad8003e0cf8309.png!small?1648783868511)

### 安全设备关联分析

基本确定攻击途径和时间后可以在以下安全设备中找相关联日志，尽最大可能还原完整攻击链路。

  * 态势感知
  * 关键路径防火墙
  * 跟本次勒索病毒入侵途径相关的设备日志

