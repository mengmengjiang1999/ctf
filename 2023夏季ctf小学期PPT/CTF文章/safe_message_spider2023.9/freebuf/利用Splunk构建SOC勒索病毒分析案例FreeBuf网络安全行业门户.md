# 零：免喷符

此乃自闭学安全的笔记记录，行文潦草，随性笔记。

# 一、Splunk是干嘛的

splunk是一款很牛逼的机器数据处理平台，工作模式跟知名开源方案elstaticsearch大差不差。通过监控、收集、拉取等各种方式去获得并存储这些数据。

根据这些数据的时间戳通过他程序本身的神秘力量进行重新索引编排，自动解析这些数据字段的键值对，形成一个个事件。利用他的搜索语言SPL（最最最最最重要的功能），对这些事件的相关字段进行搜索，对搜索结果进行可视化处理，输出报表、定时告警、仪表盘等。

# 二、splunk解决方案

splunk是闭源的。同名公司splunk也围绕splunk平台开发了各种解决方案，主要有：

![image](https://image.3001.net/images/20220809/1660039039_62f22f7f39cce5881cdce.png!small)

### 1、安全运营：

 **1.1 Splunk Enterprise Security （ES）**

最主要的平台，根据不同功能及部署架构（收、存、索引、查、运维管理）呈现不同的角色  
Splunk Enterprise（核心） 可以申请使用

splunk支持安装app，es就是个扩展APP，赋予安全功能，官方根据att&ck框架，  
#对不同日志数据编写了各种SPL查询语句，找出并定制了靓靓的安全告警仪表板，要钱

 **1.2 Splunk User Behavior Analytics （UBA）**

类似ndr，用户行为分析，一个独立的软件，通过从核心平台收集来的流量日志，

运用神秘机器学习力量进行关联分析，挖掘未知告警 返回给核心平台，要钱

 **1.3 Splunk SOAR**

自动化操作工具，通过定制自动化剧本对不同告警联动各种网络、安全设备等进行各种自动化处理

比如联动防火墙拦截IP，拦截域名等等，主要工作模式是REST API，要钱

### 2、IT运营：

 **2.1 ITSI：**

没了解过

 **2.2 Splunk VictorOps：**

没了解过

### 3、splunk-enterprise主要学习路线：

在各种平台安装splunk

导入各种数据

各种方式搜索数据

对搜索结果整理成报表或是定期告警

制作各种仪表盘，数据图

整体布局及其他运维操作

# 三、利用splunk来进行勒索病毒事件分析

### 1、主页介绍

search&report应用的界面，是splunk的核心应用，splunk的应用功能非常强大，可以安装不同的应用来实现不同功能，都是splunk官方或一些安全厂商为了让自身安全产品的日志适配splunk所开发出来的工具集。

比如checkpoint开了一个checkpoint app for
splunk，利用此app就能快速导入并解析checkpoint安全产品的日志并形成安全告警。  
![image](https://image.3001.net/images/20220809/1660039178_62f2300a139423d4fe37f.png!small)

### 2、 登入官方实例

官方提供了一个splunk- instance，用于指引安全事件排查

![image](https://image.3001.net/images/20220809/1660039296_62f230804439d0ae8c200.png!small)

左上角可以选择各种app,对于刚安装的splunk，当然最主要是上面的search&report应用，内置了核心功能，这里的dataset是官方给这个实例安装的应用，选择安全数据集应用可以看到splunk准备了两个事件案例。

案例1收集了两个ids产品产生的安全日志，主要是检测到了webshell，nessus、nmap以及红队zuo做的其他事。模拟一般的web安全事件，但是数据源已无法使用，即没有日志了。

案例2收集sysmon（进程日志）、windows日志、网络流、ids、fortigate防火墙日志，模拟入侵windows主机后实施勒索病毒攻击行为，这是非常完整的日志链。此案例还可以用，主要使用此案例来进行分析

### 3、前情提要

![image](https://image.3001.net/images/20220809/1660039404_62f230eca1f370521ab84.png!small)

根据此数据集提示，windows窗口能看到勒索信，明显中了勒索病毒，勒索病毒的特征是带有cerber标识，并找到了相关信息。  
![image](https://image.3001.net/images/20220809/1660039470_62f2312ed0124b8e738c7.png!small)

 **3.1 面临现状**

> 他是怎么进来的？渗透到哪个层面了。拿到root了？（深度，当然这里被干爆了）
>
> 只有这台主机中招吗，影响了多少主机？（广度）
>
> 病毒木马识别与清除？（主机排查）
>
> 要怎么做补救？（防御加固）

 **3.2 理清思路**

安全分析主要利用各种网络设备、网络安全软硬件，主机安全软硬件产生的日志还原黑客攻击链。

根据不同的设备角色，常见攻击入口有：

如desktop，钓鱼邮件、带毒的可移动介质等

如服务器，看服务器角色，如web服务器常见于web攻击等。

以web攻击为例，首先往往是黑客的主机与受害主机建立http链接（ip：port）。网络方面，涉及到网络流日志，边界的安全防护设备的检测日志以及ids入侵检测的日志。

流量进入到主机，我们知道，所谓连接，本质上就是两台主机之间端口所在进程的通信。比如80端口，那就是能发起http请求的客户端进程与httpd进程的通信。

当黑客通过sql注入也好，文件上传漏洞入侵httpd成功拿到shell后，实际上就是获得了httpd进程的属主账户在主机上的shell权限。接下来他可能进行外链，还是进一步提权，或是横向移动，都是以httpd进程属主身份操作的，sysmon就可以监控这些进程的行为。

拿下跳板服务器后，开始内网漫游，内网协议主要是arp发现、网络扫描、SMB、SSH、3389等

### 4\. sourcetype日志源

此案例收集了以下日志：

suricata：IDS检测日志

stream网络流日志：tcp、snmp、smb、sip、mapi、ldap、ip、icmp、http、dns、dhcp

nessus：扫描器日志

iis：http日志

Fortigate日志：utm（安全日志）、traffic（流量日志）、event（自身系统日志）

windows日志：sysmon进程监控、注册表、系统、安全、应用  
![image](https://image.3001.net/images/20220809/1660039798_62f23276d351a2a6ccfb2.png!small)

源类型是splunk用来标识不同的日志来源的。splunk内置了很多源类型，比如windows的，linux的。而Fortigate没有内置，但是厂商开发了app提供了解析正则表达式，也可以通过安装app进行日志规范化。

###
比如公司总部和子公司都用了fortigate的防火墙，他们都通过514端口推送安全日志到slunk平台，那么假设这么多台fortigate防火墙的安全日志源类型都归类到fgt_utm，此时通过splunk搜索框，就能搜索出所有的fortigate的安全日志，就能一次性统筹查看公司整体网络边界防火墙的各种安全数据

如何分辨是哪一台防火墙的日志呢。其实在发送给splunk那一刻，splunk对其进行索引，就记录下源主机ip，存到host字段中如果不加host筛选，或者host=*，那就搜索所有的安全日志  
`sourcetype = fgt_utm host=*`

# 四、正式开始调查

### 1、调查受害主机

我们知道受害主机名是we8105desk，这里并没有使用指定字段搜索，也就是模糊搜索相关字符串

index是botsv1，index是一个重要的过滤条件，基本所有的搜索都是从它开始的。比如该公司存在多个分部，广州、北京、上海等等，那么通常会为各个分部建立一个index，那么当index=guangzhou时，就会快速搜索广州到广州的数据，而不是搜索全部，加快搜索速度

这个案例的index是botsv1

`index=botsv1 we8105desk`

 **1.1查找we8105desk主机信息**

通过查找sysmon的操作日志并进行主机名模糊搜索，根据源地址进行统计出现次数并排序，得知绝大多数ip是192.168.250.100，此IP很可能就是受害主机的IP地址  
`index=botsv1 we8105desk sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational | stats count by src_ip | eventstats sum(count) as perc |
eval percentage=round(count*100/perc,2) | fields - perc | sort - count`  
![image](https://image.3001.net/images/20220809/1660040154_62f233dabec820ac36ab5.png!small)

同时通过sysmon里的src_host字段值出现的we8105desk.waynecorpinc.local次数与ip出现次数大致相同可以进行确认，此时的主机信息是：  
![image](https://image.3001.net/images/20220810/1660095132_62f30a9c67c3465762172.png!small)

 **1.2 USB取证**

由于是台desktop，不太可能开放了web或其他服务被人打进来，注意力放在windows自身的日志，会不会是从usb可移动介质引起的安全事件呢。有时，我们需要知道哪些
USB 设备连接到到该计算机。

注册表是 Windows 中的一个数据库，用于存储操作系统、硬件设备、软件程序和用户偏好设置的设置。每当我们将 USB
驱动器插入计算机时，都会创建一个名为“USBSTOR”的注册表项。此注册表项存储有关该 USB
设备的信息，操作系统需要知道的任何信息都可以在此注册表项中找到  
`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Enum\USBSTOR`

使用splunk进行模糊搜索friendlyname，找到了两条json格式的日志，指定index，指定了数据源是注册表日志  
`index=botsv1 sourcetype=winregistry friendlyname`  
![image.png](https://image.3001.net/images/20220810/1660095467_62f30beb17e746097bf95.png!small)

json格式日志非常不直观，splunk做了解析，并把解析到的字段展示在左边的字段选择区，我们对这两个事件的相关进行列出，可以看到确实与该主机相关。

使用管道符将数据传递给table 命令，table是制表命令，后面跟想要的字段  
`index=botsv1 sourcetype=winregistry friendlyname | table host object data`  
![image.png](https://image.3001.net/images/20220810/1660095543_62f30c371f82fd1544327.png!small)

此时从data字段查到了usb设备名  
![image.png](https://image.3001.net/images/20220810/1660095584_62f30c60ed6469c54c1fb.png!small)

 **1.3 进程取证**

U盘插入计算机释放了恶意文件，执行命令，会创建进程活动。找出异常文件、可疑命令和可疑进程  
`index=botsv1 sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
host=we8105desk`  
![image.png](https://image.3001.net/images/20220810/1660095726_62f30ceef038d06c37560.png!small)

发现很多的C盘路径的命令，U盘盘符肯定不是C盘，所以排除C盘开头的，只看到一个D盘，使用模糊搜索D盘的相关指令，找出了执行奇怪命令，比如打开了121214.tmp、20429.vbs  
![image.png](https://image.3001.net/images/20220810/1660095796_62f30d341fe11527272b6.png!small)

精确搜索D盘插入时，由D盘开始打开了啥文件并执行，可以看到是用word程序打开了文件，然后就被执行了这一堆奇怪代码，明显是U盘存在带毒的word文档  
`index=botsv1 sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
host=we8105desk (CommandLine="*d:\\*" OR ParentCommandLine="*d:\\*") | table
_time CommandLine ParentCommandLine | sort _time`  
![image.png](https://image.3001.net/images/20220810/1660095886_62f30d8e31aad75a68186.png!small)  
![image](https://image.3001.net/images/20220810/1660095984_62f30df039d4d56a6ee00.png!small)

 **1.4 排查主机的主要横向活动**

查看操作日志找出这个主机有没有进行横向扩散  
发现和192.168.250.20、192.168.2.50这两个IP地址的连接数远远高于其他IP  
![image.png](https://image.3001.net/images/20220810/1660096140_62f30e8ca4ef2a7d7f842.png!small)

查找注册表日志，模糊搜索fileshare发现和192.168.250.20存在文件共享  
![image.png](https://image.3001.net/images/20220810/1660096212_62f30ed4019b33649112d.png!small)

对192.168.250.20进行主机名识别，同时搜索该主机源主机和目的主机时出现次数最多的主机名，大致得到主机名是we9041srv.waynecorpinc.local，从主机名得知这是一台服务器  
`index=botsv1 sourcetype="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"
192.168.250.20 | stats count by src_host | eventstats sum(count) as perc |
eval percentage=round(count*100/perc,2) | fields - perc | sort - count
index=botsv1 sourcetype="XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"
192.168.250.20 | stats count by dest_host | eventstats sum(count) as perc |
eval percentage=round(count*100/perc,2) | fields - perc | sort - count`  
![image.png](https://image.3001.net/images/20220810/1660096287_62f30f1f7a305ef6d0117.png!small)

### 2.多方位排查

 **2.1 排查外链情况**

查找主机是否进行外链，DNS的A记录能帮到我们，DNS的A记录是指向DNS发起解析请求，解析某个FQDN的IP地址。  
`index=botsv1 sourcetype=stream:DNS src=192.168.250.100 record_type=A`  
![image.png](https://image.3001.net/images/20220810/1660096371_62f30f739ff3dd6cc106f.png!small)

发现DNS查询记录有很多Microsoft的主机地址，他不太可能搞我们，排除掉，同时排除内部地址，查询wpad、isatap是正常，都排除，只剩下了三个域名，其中两个很奇怪，先连接了solidaritedeproximite.org、后连接cerberhhyed5frqa.xmfir0.win，同时
发现是向192.168.250.20发起的DNS请求，目的地址很可能是DNS服务器  
`index=botsv1 sourcetype=stream:DNS src=192.168.250.100 record_type=A NOT
(query{}=*.microsoft.com OR query{}=*.waynecorpinc.local OR query{}=*.bing.com
OR query{}=isatap OR query{}=wpad OR query{}=*.windows.com OR
query{}=*.msftncsi.com) | table _time query{} src dest | reverse`  
![image.png](https://image.3001.net/images/20220810/1660096454_62f30fc68de02a7825fb8.png!small)  
![image.png](https://image.3001.net/images/20220810/1660096512_62f310007cb19a62d11b9.png!small)

 **2.2 查询相关勒索软件信息**

通过查询安全厂商信息，得知该恶意软件会进行http下载恶意文件，于是排查http连接情况  
![image](https://image.3001.net/images/20220810/1660096631_62f310777d72112b048f4.png!small)

 **2.3 流日志查询**

查询流日志确实发现了相关文件URL

stats 是统计命令，stats count是统计搭配，如果写成`stats count by dest
url`那么dest和url组成了很多种唯一值，往往是dest相同，url不同。会出现很多条

使用values就是将多值字段合并到一个格子形成1对多的关系  
`index=botsv1 sourcetype=stream:http src=192.168.250.100 mhtr | stats count
values(url) by dest`  
![image.png](https://image.3001.net/images/20220810/1660096748_62f310ecc9a1a4adf8331.png!small)

 **2.4 IDS日志查询**

查询suricata IDS的日志也发现相似结果  
![image.png](https://image.3001.net/images/20220810/1660096852_62f3115491fdeaee6fe5d.png!small)

 **2.5 查询微步**

查询微步，相关URL确实是勒索软件  
![image.png](https://image.3001.net/images/20220810/1660096927_62f3119f3b3e643f28599.png!small)

 **2.6 UTM日志查询**

查询utm的日志，发现192.168.250.100连接到相关地址进行下载mhtr.jpg文件，action是allowed，也就是没有阻挡  
`index=botsv1 sourcetype=fgt_utm src=192.168.250.100 mhtr.jpg | table _time
src dest msg url action`

![image.png](https://image.3001.net/images/20220810/1660096993_62f311e158a6c8962f75f.png!small)

继续在utm排查192.168.250.100的后续行为，共有9640个事件,从app字段中看到9231个都跟Cerber.Botnet有关，明显是下载了jpg文件后被控了  
![image.png](https://image.3001.net/images/20220810/1660097065_62f312293cd5ee0fc59f3.png!small)  
![image.png](https://image.3001.net/images/20220810/1660097214_62f312beb00be22edd5ad.png!small)

 **2.7 进程调用排查**

那么受害主机上有多少恶意进程呢，以及进程之间怎么调用的

排查一下刚才提到的12114.tmp，查看下这个文件究竟怎么来的，做了啥还是排查sysmon的日志，模糊搜索，找出父进程子进程的ID以及命令  
`index=botsv1 sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
121214.tmp CommandLine=* | table CommandLine ProcessId ParentProcessId
ParentCommandLine | reverse`  
![image.png](https://image.3001.net/images/20220810/1660097406_62f3137e050f3a1afb4b1.png!small)

可以看到是由20429.vbs打开121214.tmp，这个看似临时的文件居然会执行命令，调用了osk.exe，还做了计划任务管理

同理，那么20429.vbs被谁调用过呢，其实就是那戳很复杂的命令来的,继续模糊搜索，名字替换为这个VBS  
![image.png](https://image.3001.net/images/20220810/1660097545_62f31409a2330fc75a6f3.png!small)

而osk.exe则是做了更多事情，以及写下了勒索信  
![image.png](https://image.3001.net/images/20220810/1660097599_62f3143f9965d109ce760.png!small)

### 3\. 损失面统计

 **3.1 排查文件被加密情况**

究竟加密了多少文件，可以查看sysmon，查询到其日志里的EventCode种类，有1、2、3、5、6、7  
`index=botsv1 sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
host=we8105desk |stats count by EventCode`  
![image.png](https://image.3001.net/images/20220810/1660097711_62f314af26ed2b4207e02.png!small)

涉及文件操作的只有2和7,7是图像加载，重点是2，文件创建时间，当文件创建时间被进程显式修改时，会注册更改文件创建时间事件。此事件有助于跟踪文件的实际创建时间。攻击者可能会更改后门的文件创建时间，使其看起来像是随操作系统一起安装的。请注意，许多进程会合法地更改文件的创建时间；它不一定表示恶意活动。

发现EventCode为2的事件中，1179个文件更改事件中大部分都跟osk.exe和121214.tmp有关，看来这些文件都被加密了。  
`index=botsv1 sourcetype=XmlWinEventLog:Microsoft-Windows-Sysmon/Operational
host=we8105desk EventCode=2`  
![image.png](https://image.3001.net/images/20220810/1660097818_62f3151abd19754ab6077.png!small)

排查文件服务器的文件是否被远程加密，排查步骤同理。

### 4、总结

 **4.1 事件概括**

用户（或某人）将受感染的 USB 驱动器插入 Bob Smith 的工作站

Word 文档产生了一个可疑进程，该进程产生了其他进

外链FQDN 和 IP 地址后下载文件

文件加密在本地磁盘和共享上开始

重定向到带有加密通知的外部站点  
**![image.png](https://image.3001.net/images/20220810/1660097951_62f3159f7d4571eb2b3c1.png!small)**

 **4.2 splunk使用总结**

splunk是一个强大的日志管理平台，通过官方的SPL搜索语句，可以实现非常强大的数据透视。

使用splunk进行安全分析，取决于日志种类的丰富程度，以及日志量的多少

splunk内置了各种APP智能解析市面上知名的安全产品

对于其他厂商可以自行开发APP适配splunk平台

