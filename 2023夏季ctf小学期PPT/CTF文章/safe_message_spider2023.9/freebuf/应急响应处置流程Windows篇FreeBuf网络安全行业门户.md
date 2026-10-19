**文档在自己的文件夹静静的躺了快半年了，好吧，先把应急响应流程步骤（乙方视角）和windows拆出来，在进行应急响应事件处置时需严格遵守公司的应急响应制度。**

## 一、 **服务流程** ****

###  **沟通确认安全事件** ****

在与客户第一次沟通时，应及时提醒客户对受害机器及时进行断网隔离操作。已知的安全事件包括但不限于如下：

> 1\. 恶意代码威胁，即僵尸网络、恶意木马、蠕虫病毒、勒索病毒等恶意代码导致的安全事件
>
> 2\. 高级持续性威胁(APT)攻击事件，即具有潜伏性、隐蔽性、目的性、持续性等特点的安全事件
>
> 3\.
> 非法入侵事件，包括但不限于业务系统受到入侵致使数据泄露、丢失等；外网网站被入侵，导致网站被恶意篡改植入暗链或出现其他非法的宣传标语；服务器被入侵导致受到勒索攻击等安全事件
>
> 4\. 漏洞事件，即0day公布；在野漏洞发现；已知漏洞被发现受到通报等安全事件
>
> 5\. 数据泄露事件，即重要数据因受到了入侵导致的泄露；应用配置不当导致的泄露；员工误操作导致的泄露；内鬼泄露等安全事件
>
> 6\. 分布式拒绝服务攻击（DDOS）事件，即网站受到了各类DOS攻击，包括但不限于CC攻击、洪水攻击、流量放大攻击等安全事件
>
> 7\. 流量劫持，DNS劫持、HTTP劫持
>
> 8\. 其他归于网络安全的事件

注意事项：一定要亲自确认，切不可盲目相信他人所述。

确认后，应尽量收集与本次安全事件相关的信息，例如什麽时候发现的攻击，之前有无出现过安全事件等。

在确认安全事件后明确应急目的：

> 1\. 病毒、后门清除工作
>
> 2\. 协助业务系统安全的恢复上线
>
> 3\. 攻击溯源工作。（仅溯源至攻击者的攻击切入点）

###  **现场保护** ****

在与客户沟通时，应提醒客户注意保护现场，千万不要直接重装系统，以方便后续的溯源工作及可能存在的电子取证工作。在处置受害机器时，应尽量保持受害机器的原样，如虚拟机处置时，可以让客户进行快照存储。

###  **了解客户网络状况** ****

对客户的网络拓扑应尽早进行了解，特别是网络的进出口、负载均衡、防火墙、DNS服务器。

###  **确定事件影响** ******确定工作方向** **确立工作目标** ****

###  **明确现场工作任务归属** ****

无论现场的环境，主导本次安全事件，合理分配现场工作为应急人员的必备技能。

对现场的可能存在的工作应具备清晰的认知。通常会存在以下工作内容：病毒分析处置、业务恢复、安全加固、溯源分析、临时需求处置、产品对接与使用、应急指挥与协调。

## 二、 **技术部分** ****

### 1. **系统** ****

1.1 **Windows** ****

1.1.1 熟悉现场环境 ****

对受害机器进行了解，分析可能存在的共同弱点，进而提供溯源思路。

如：是否存在弱口令（例如3389、FTP、中间件、数据库）

是否存在对外映射的端口，或WEB应用等

1.1.2 账号安全风险分析 ****

查看当前已登录的账号

query user

![图片.png](https://image.3001.net/images/20190514/1557816299_5cda63eb589d4.png!small)使用logoff
ID 命令注销已登录用户，当可疑账号处于登录状态时，也可以使用mimikatz抓取密码。

![图片.png](https://image.3001.net/images/20190514/1557816961_5cda668160a00.png!small)

查看用户目录 是否存在新建用户目录

    
    
    C:\Documents and Settings
    
    C:\Users

查看对应用户的desktop与download目录下是否存在异常文件

![图片.png](https://image.3001.net/images/20190514/1557816969_5cda668947dd6.png!small)![图片.png](https://image.3001.net/images/20190514/1557816976_5cda6690072b4.png!small)

查看是否存在可疑账号、新增账号（注意Guest用户是否开启）

Win+R输入lusrmgr.msc net user username查看详细

![图片.png](https://image.3001.net/images/20190514/1557816982_5cda6696a912c.png!small)

查看是否存在隐藏账号、克隆账号

运行 -- regedit.exe查看注册表

![图片.png](https://image.3001.net/images/20190514/1557816991_5cda669f0e374.png!small)![图片.png](https://image.3001.net/images/20190514/1557816996_5cda66a44325e.png!small)

或使用工具PC hunter与D盾进行排查

建立隐藏用户参考链接：

<https://www.cnblogs.com/lunachy/p/4602228.html>

1.1.3 日志风险分析 ****

Win+R 输入 eventvwr.msc

打开事件查看器，注意日志事件是否存在缺失现象（日志出现断点或发现存在清除痕迹）。

日志事件查看器本身支持筛选功能。也可以导出为CSV 或者TXT使用Excel或者Notepad进行分析  

> 使用微软Log Parser进行分析（Log ParserUI封装了语句gui界面）
>
> 运行 -- %UserProfile%\Recent，分析最近打开可疑文件，或根据最近修改时间进行排查
>
> 查看U盘使用痕迹，对比各时间点，排查可疑使用记录

 _//*注意采集日志时，应注意日志是否存在时间断点、或部分日志丢失情况_

1.1.4 病毒风险排查 ****

> 使用360杀毒离线版，并下载最新病毒库下载地址：<http://sd.360.cn/download_center.html>
>
> 使用其他杀软，并注意客户现场是否存在友商产品。

1.1.5 异常风险分析 ****

1.1.5.1端口状态 ****

> cmd命令
>
> netstat -ano
>
> netstat -ano | findstr “port”查看端口对应的活动连接
>
> tasklit | findstr “PID” 查看相应PID的进程

![图片.png](https://image.3001.net/images/20190514/1557817027_5cda66c3503fd.png!small)

TCP端口状态说明

![图片.png](https://image.3001.net/images/20190514/1557817040_5cda66d093b7d.png!small)

<https://www.cnblogs.com/jessezeng/p/5617105.html>

 **工具使用**

PC Hunter、D盾

1.1.5.2进程 ****

运行 -- msinfo32 --软件环境--正在运行任务，查看详细

![图片.png](https://image.3001.net/images/20190514/1557817049_5cda66d96018f.png!small)

运行 -- taskmgr 任务管理器进行查看，可由进程打开相应文件位置，及相应服务。

排查可疑进程及子进程（多涉及感染型病毒）

观察内容包括：

> 没有签名验证信息的进程
>
> 没有描述信息的进程
>
> 属主异常的进程
>
> 路径不合法的进程
>
> CPU或内存资源 长时间或过高占用的进程
>
> 存在异常活动连接的进程

 **工具使用：** ****

PC Hunter、D盾、Process Explorer、Process Hacker、Autoruns

1.1.5.3启动项 ****

注意当前系统时间是否有问题，病毒可能存在篡改系统时间，或利用系统时间异常的可能性。

单击--开始--所有程序--启动

![图片.png](https://image.3001.net/images/20190514/1557817059_5cda66e3a501e.png!small)

输入命令查看启动项wmic startup list full

运行 -- 输入msconfig查看是否存在可疑的启动项目

![图片.png](https://image.3001.net/images/20190514/1557817066_5cda66eaadf92.png!small)

打开注册表，查看是否存在可疑开机启动项，特别注意如下三个注册表项：

> HKEY_CURRENT_USER\software\micorsoft\windows\currentversion\run
>
> HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
>
> HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Runonce

![图片.png](https://image.3001.net/images/20190514/1557817075_5cda66f3803a2.png!small)

运行 -- gpedit.msc组策略中查看启动

 **工具使用** **:** ****

Autoruns、PC Hunter、360安全卫士

1.1.5.4计划任务 ****

控制面板 -- 管理工具 -- 任务计划程序

或运行 -- taskschd.msc

通过命令查看计划任务schtasks /query /fo table /v

![图片.png](https://image.3001.net/images/20190514/1557817110_5cda6716413a3.png!small)![图片.png](https://image.3001.net/images/20190514/1557817092_5cda670443e7a.png!small)

或者注册表下手动排查（其使用了XML格式，若出现特殊字符，可导致打开报错）

    
    
    HKEY_LOCAL_MACHINE \ SOFTWARE \ Microsoft \ Windows NT \ CurrentVersion \ Schedule \ TaskCache \ Tree

![图片.png](https://image.3001.net/images/20190514/1557817116_5cda671ce7594.png!small)

运行 -- 管理员运行cmd -- at 检查计算机与网络上其他计算机之间的会话或者计划任务，如有确认是否为正常连接。

1.1.5.5系统服务 ****

运行 -- services.msc 注意服务状态和启动类型，检查是否存在可疑服务。

运行 -- taskmgr 任务管理器内查看服务

 **工具使用：** ****

PC Hunter

1.1.6 系统风险分析 ****

1.1.6.1 系统后门排查 ****

对当前操作系统版本、操作系统补丁、应用版本进行确认，分析可能存在的威胁因素。

如“永恒之蓝”漏洞未打补丁，是否存在利用痕迹。

IIS低版本漏洞。

检查方法：

> 1\. 运行 -- systeminfo查看系统信息
>
> 2\. Shift后门排查使用OD 分析C:\WINDOWS\system32\dllcache\sethc.exe
>
> 3\. 对于一些windows常见的持久化痕迹基本都很明显，如有需要可以参考
>
> <https://www.freebuf.com/vuls/195906.html>

1.1.6.2 敏感目录排查 ****

可能存在问题的敏感目录

    
    
       %WINDIR%
    
    %WINDIR%\system32%TEMP%
    
    %LOCALAPPDATA%
    
    %APPDATA%
    
    各盘下的tmp缓存目录，例如C:\Windows\Temp

1.1.7 综合分析得出结论 ****

> 1\. 系统漏洞直接造成的入侵事件。如“永恒之蓝”、弱口令
>
> 2\. 系统漏洞间接造成的入侵事件。如WebShell后，本地提权。
>
> 3\. 应用漏洞直接或间接造成的入侵事件。如Struts 2远程命令执行、WebLogic弱口令或远程代码执行、IIS
> PUT上传漏洞、FTP弱口令或溢出攻击等。

 ***本文作者：PinkWolf，转载请注明来自FreeBuf.COM**

