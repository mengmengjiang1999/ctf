# 一、事件发生背景

办事处部署的TAR产生挖矿告警，如下图（1）TAR挖矿告警所示。告警显示是售前用来存储文件的服务器（IP：10.33.15.240）中了CoinMiner挖矿病毒。![](https://image.3001.net/images/20220219/1645233089_621043c1db48cfff5b845.png!small)

图（1）TAR挖矿告警

# 二、初步排查判断

通过分析TAR设备告警，登录相关服务器进行排查。使用命令cmd-netstat
-ano。![](https://image.3001.net/images/20220219/1645233109_621043d51da92fe5c7330.png!small)

图（2）命令执行结果

根据TAR提供的矿池地址，查找此服务器的TCP连接，成功定位相关PID为696，如上图（2）命令执行结果所示。

根据PID 696使用命令tasklist | findstr “696”确定运行的恶意服务。成功找到相关PID运行的恶意exe，如下 图（3）恶意exe
所示。

![](https://image.3001.net/images/20220219/1645233142_621043f6399b126a01447.png!small)

图（3）恶意exe

使用命令wmic process where processid=696 get
processid,executablepath,name，成功确定恶意exe文件的位置，如下图（4）恶意exe路径 和 图（5）恶意exe文件 所示。

![](https://image.3001.net/images/20220219/1645233157_62104405f0b0be2757840.png!small)

图（4）恶意exe的位置

![](https://image.3001.net/images/20220219/1645233191_62104427568b919db1359.png!small)图（5）恶意exe文件

对相关恶意exe在微步云沙箱中检测，分析结果和TAR告警一致，如下图（6）微步沙箱检测所示。

![](https://image.3001.net/images/20220219/1645233262_6210446e1eceabc7ec69a.png!small)

图（6）微步沙箱检测

使用火绒对服务器进行查杀，查杀结果如下图（7）火绒查杀结果
所示。![](https://image.3001.net/images/20220219/1645233279_6210447f278f1b666c780.png!small)

图（7）火绒查杀结果

# 三、追踪溯源

查看相关服务器安全日志，发现自2021.11.30 11.40
开始，有大量事件ID为4625的事件记录，源IP为10.33.15.164，使用的账户名为vneus，失败原因账户密码过期。如下图（8）Windows安全日志所示。Windows事件ID
4625记录的是每一个尝试登录失败本地计算机的事件，无论登录类型、用户的位置、账户。![](https://image.3001.net/images/20220219/1645233355_621044cb67feb71a9d395.png!small)

图（8）Windows安全日志

初步判定是内网相关主机感染病毒之后，病毒程序通过爆破SMB服务，将病毒传染给此服务器。继续分析安全日志，发现在2021.12.01
15:54:25，源IP为10.33.52.50的用户通过venus用户成功登录服务器，如下图（9）Windows安全日志所示。![](https://image.3001.net/images/20220219/1645233375_621044df74325db287480.png!small)

图（9）Windows安全日志

此时vneus用户密码更新，在2021.12.01
17:15:31，源IP为10.33.53.164的内网主机成功爆破出venus账户密码，如下图（10）Windows安全日志所示。![](https://image.3001.net/images/20220219/1645233401_621044f94d5a373a68ced.png!small)

图（10）Windows安全日志

10.33.15.164无权限查看，等申请之后在进行溯源。

# 四、事件原因分析。

结合WannaMine 4.0挖矿病毒特性，事件原因分析如下：

  1. 内网主机33.53.164感染WannaMine 4.0挖矿病毒后，病毒程序爆破目标服务器venus用户密码。
  2. venus账户密码过期，爆破一直失败。
  3. 期间有人员正常使用venus用户登录服务器，更新了venus账户密码。
  4. 此时病毒程序成功爆破出venus账户密码。
  5. 病毒程序通过445端口的SMB服务成功将病毒传播给此服务器。

# 五、改进建议

## 5.1 关闭445端口

  1. 点击 “控制面板-Windows防火墙”，确保启用了Windows防火墙。在左边栏点击“高级设置”，系统会自动弹出Windows防火墙高级配置窗口。
  2. 点击“入站规则”，然后再点“新建规则”，在向导窗口中选择要创建的规则类型，选“端口”，点击“下一步”。
  3. 接下来选择你要禁用的网络类型（TCP或者UDP），在“特定本地端口”写入你要禁用的端口，例如“445”，然后下一步。选择“阻止连接”，下一步，应用规则看情况修改，可以维持不变，继续下一步，填写名称“禁用445端口”，点击完成。

## 5.2 修改RDP协议默认端口

  1. 打开注册表。
  2. 找到HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Terminal Server \Wds\rdpwd\Tds\Tcp下PortNumber键的键值：0xd3d，是16进制，也就是10进制的3389，也就是RDP协议的端口，改成你欲设的端口。
  3. 找到HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\TerminalServer \WinStations\RDP-Tcp下PortNumber键的键值：0xd3d，是16进制，也就是10进制的3389，也就是RDP协议的端口，改成你欲设的端口（必须与第一步修改的一致）。
  4. 重启电脑。

# 六、WannaMine 4.0挖矿病毒

## 6.1 简介

CoinMiner是WannaMine挖矿病毒最新变种文件，该变种文件基于WannaMine3.0改进，加入了一些新的免杀技术和爆破手段，其传播机制与WannaCry勒索病毒一致，可在局域网内通过SMB快速横向扩散，我们将其命名为WannaMine
4.0，其检测名为CoinMiner.Win64.TOOLXMR.AR。WannaMine4.0挖矿主体病毒文件为dllhostex.exe，负责挖取门罗币。

原始“压缩包”rdpkax.xsl含有攻击需要的所有组件，其是一个特殊的数据包，需要病毒自己解密分离出各个组件，其组件包含“永恒之蓝”漏洞攻击工具集（svchost.exe、spoolsv.exe、x86.dll/x64.dll等）。

## 6.2 攻击流程

  1. 主服务dll由系统进程加载，以确保每次都能开机启动，启动后加载spoolsv.exe。
  2. exe对局域网进行445端口扫描，确定可攻击的内网主机。同时启动漏洞攻击程序svchost.exe。
  3. exe执行“永恒之蓝”漏洞攻击，成功后安装后门程序spoolsv.exe，加载payload（x86.dll/x64.dll）。
  4. payload（dll/x64.dll）执行后，复制rdpkax.xsl到目标主机，解密后注册主服务，进行新的攻击，每一台被攻击机器都重复着同样的攻击流程。
  5. 与0不同的是，该变种使用了服务文件名称和内容的随机行来进行免杀，进而payload文件与之前版本相比也发生了变化。主服务的命名规则为“字符串1+字符串2+字符串3”，如上面提及的RemoteTimeHost，即Remote+Time+Host。

## 6.3 如何防范

  1. 利用系统防火墙高级设置阻止向445端口进行连接（该操作会影响使用445端口的服务，关闭方法见改进意见）。
  2. 尽量关闭不必要的文件共享；
  3. 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
  4. 打开系统自动更新，并检测更新进行安装。
  5. 系统打上MS17-010对应的Microsoft Windows SMB服务器安全更新(4013389)补丁程序。

