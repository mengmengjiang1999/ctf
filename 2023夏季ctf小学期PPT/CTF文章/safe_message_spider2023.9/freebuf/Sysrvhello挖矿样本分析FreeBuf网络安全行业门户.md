## 概述

数字货币价格再现剧烈波动，这场狂热者的财富游戏总是不乏恶意矿工的身影。近日， **奇安信安全能力中心** 通过 **TG-DATA** **威胁分析平台**
捕获到Sysrv-hello挖矿蠕虫最新变种，变种编号007。

sysrv007通过漏洞攻击方式植入目标主机。在努力尝试占据系统最大化资源后，释放其自身挖矿模块，并通过进程守护确保挖矿程序的不间断工作；最后通过端口扫描与漏洞利用传播自身。

![1616384477_605811dd49daac6761faf.png!small?1616384477543](https://image.3001.net/images/20210322/1616384477_605811dd49daac6761faf.png!small?1616384477543)

图 1. sysrv007攻击流程

相较之前捕获的sysrv003样本，sysrv007对其基础设施进行了更新，自身传播能力也有所加强。sysrv007利用的漏洞数量相较以往增长了1倍。成倍的漏洞数量意味着挖矿蠕虫更强大的传播能力以及更广泛的传播范围。短时间内的快速迭代亦展现了其背后开发者的分外活跃。

## 样本分析

### 下载执行

sysrv-hello渗透进目标主机后，从hxxp://194.40.243.98/ldr.ps1下载并执行恶意PowerShell脚本。

![1616384499_605811f32a53fb899795f.png!small?1616384499391](https://image.3001.net/images/20210322/1616384499_605811f32a53fb899795f.png!small?1616384499391)

图 2. 恶意脚本文件ps1

恶意PowerShell脚本的功能为下载并执行主模块sysrv007.exe。sysrv007被UPX加壳，本体为使用1.9.2版本SDK编译的Go程序。此外，观察样本的编译文件路径可以发现：病毒作者的用户名为‘k’。

![1616384507_605811fbbc6bedc376445.png!small?1616384508011](https://image.3001.net/images/20210322/1616384507_605811fbbc6bedc376445.png!small?1616384508011)

图 3. sysrv007文件路径

### 自我更新

sysrv007运行后，首先结束掉sysrv自身的老版本进程。

![1616384520_6058120848161f9cfdc60.png!small?1616384520564](https://image.3001.net/images/20210322/1616384520_6058120848161f9cfdc60.png!small?1616384520564)

图 4. 被杀死的sysrv进程名

然后判定本地52016端口开启情况。默认端口开启状态为已感染状态；端口关闭则占用之、并使用该端口号创建互斥量。

![1616384528_605812102a2ccc6f08d46.png!small?1616384528846](https://image.3001.net/images/20210322/1616384528_605812102a2ccc6f08d46.png!small?1616384528846)

图 5. 创建互斥量

接着，sysrv007杀死占用系统资源较多的其他进程，从而使自身最大限度的占用系统计算资源。观察发现：被杀死的进程名中，大部分为其他家族挖矿进程，扫描监控类进程。

![1616384536_6058121810d4201c40584.png!small?1616384536303](https://image.3001.net/images/20210322/1616384536_6058121810d4201c40584.png!small?1616384536303)

图 6. 被杀掉的进程名称

最后，sysrv007创建挖矿守护线程，每50秒触发一次。当系统没有运行其门罗币挖矿程序时：守护线程释放挖矿程序[kthreaddi].exe和配置文件config.json至Temp目录，并运行。挖矿进程启动后，配置文件随即删除。

![1616384544_60581220ead4d749bf766.png!small?1616384545276](https://image.3001.net/images/20210322/1616384544_60581220ead4d749bf766.png!small?1616384545276)

图 7. 释放挖矿模块

![1616384551_6058122787bd495c18079.png!small?1616384551774](https://image.3001.net/images/20210322/1616384551_6058122787bd495c18079.png!small?1616384551774)

图 8. 挖矿配置文件json

### 恶意传播

sysrv007在受害主机达成其挖矿的主要目的后，并不满足于此。开始通过其内置的端口扫描与漏洞利用模块在网络上传播自身。

sysrv007的端口扫描模块随机生成待扫描IP，并通过SYN扫描的方式判断目标主机的端口开放情况，每个端口扫描3分20秒。扫描的端口列表如下图所示。

![1616384563_60581233c0e54f04ea137.png!small](https://image.3001.net/images/20210322/1616384563_60581233c0e54f04ea137.png!small)

图 9. 扫描的端口列表

![1616384574_6058123e60f9d5e578fff.png!small?1616384574664](https://image.3001.net/images/20210322/1616384574_6058123e60f9d5e578fff.png!small?1616384574664)

图 10. 端口扫描

当扫描结果发现目标主机开放了指定端口后，sysrv007通过其漏洞利用模块尝试渗透目标主机。相较近期捕获的sysrv003样本，sysrv007使用的漏洞情况如下表所示。

表1 sysrv007漏洞使用情况

 **保留漏洞模块**

|

 **新增漏洞模块**  
  
---|---  
  
Jupyter未授权访问

|

Hadoop未授权访问  
  
Nexus未授权访问

|

XXL-JOB未授权访问  
  
Tomcat未授权访问

|

ThinkPHP5 RCE  
  
WordPress未授权访问

|

CVE-2017-11610  
  
Jenkins RCE

|

CVE-2019-10758  
  
Apache solr RCE

|

CVE-2020-16846  
  
WebLogic未授权访问

|

CVE-2021-3129  
  
保留的漏洞模块中，sysrv007对针对Jenkins、Apache
solr、WebLogic的漏洞攻击模块进行了小幅修改。下面对所有涉及的漏洞攻击模块分别进行描述。

### Jupyter未授权访问漏洞

Jupyter默认监听在8888端口。如果管理员没有为Jupyter Notebook配置密码，将导致未授权访问漏洞。

![1616384628_605812744d758f33d1930.png!small?1616384628745](https://image.3001.net/images/20210322/1616384628_605812744d758f33d1930.png!small?1616384628745)

图 11. Jupyter漏洞检测

若目标存在该Jupyter漏洞， sysrv007利用该漏洞下载并执行后续恶意PowerShell载荷。

![1616384635_6058127b4c188cf93c35f.png!small?1616384635605](https://image.3001.net/images/20210322/1616384635_6058127b4c188cf93c35f.png!small?1616384635605)

图 12. Jupyter Exploit

恶意载荷下载地址如下图所示。

![1616384643_6058128382a3185aa455e.png!small](https://image.3001.net/images/20210322/1616384643_6058128382a3185aa455e.png!small)

图 13. Jupyter Payload

### Nexus未授权访问漏洞

Nexus默认端口号为8081。如果管理员设置的账户密码不够健壮，将导致远程代码执行。

![1616384656_60581290bcb2b27b5f7f6.png!small?1616384657056](https://image.3001.net/images/20210322/1616384656_60581290bcb2b27b5f7f6.png!small?1616384657056)图
14. Nexus Exploit

对于Nexus漏洞攻击模块，sysrv007相较sysrv003无明显变化。

![1616384686_605812ae808e472e1fe54.png!small?1616384686770](https://image.3001.net/images/20210322/1616384686_605812ae808e472e1fe54.png!small?1616384686770)

图 15. sysrv003 vs sysrv007(Nexus）

### Tomcat未授权访问漏洞

Tomcat 默认端口号为8080。支持在后台部署war包，若后台密码设置过于简单，则会被利用上传WebShell。

![1616384729_605812d9282f9ec390d27.png!small?1616384729437](https://image.3001.net/images/20210322/1616384729_605812d9282f9ec390d27.png!small?1616384729437)

图 16. Tomcat漏洞检测

对于Tomcat漏洞攻击模块，sysrv007相较sysrv003变化不大。

![1616384734_605812de7eabc313678f9.png!small?1616384735133](https://image.3001.net/images/20210322/1616384734_605812de7eabc313678f9.png!small?1616384735133)

图 17. sysrv003 vs sysrv007(Tomcat）

### WordPress未授权访问漏洞

WordPress默认监听在80端口。如果WordPress管理员口令设置得过于简单，攻击者可以轻易破解口令，并登录到系统，继而通过修改主题或上传含漏洞插件的方式进一步入侵受害主机。

![1616384740_605812e4f221faadc91ff.png!small?1616384741363](https://image.3001.net/images/20210322/1616384740_605812e4f221faadc91ff.png!small?1616384741363)

图 18. hello_exp_wordpress_WpExec

### Jenkins RCE

Jenkins默认端口号为8080。Jenkins允许用户通过URL
PATH调用public方法，攻击者可通过构造特殊PATH来执行一些敏感指令。在含有CVE-2018-1000861漏洞的版本中，未授权用户可以绕过Groovy沙盒执行任意命令。

下图为Jenkins用于爆破的部分用户名和密码。

![1616384745_605812e9117f273603a01.png!small?1616384745339](https://image.3001.net/images/20210322/1616384745_605812e9117f273603a01.png!small?1616384745339)

图 19. Jenkins 爆破弱口令

下图为sysrv003与 sysrv007的Jenkins攻击模块对比。

![1616384747_605812ebeac77fb8931e6.png!small?1616384748292](https://image.3001.net/images/20210322/1616384747_605812ebeac77fb8931e6.png!small?1616384748292)

图 20. sysrv003 vs sysrv007(Jenkins）

sysrv007新增CVE-2018-1000861模块。漏洞成功利用将执行恶意PowerShell命令。

![1616384752_605812f03d8eef3a15cc7.png!small?1616384752591](https://image.3001.net/images/20210322/1616384752_605812f03d8eef3a15cc7.png!small?1616384752591)

图 21. Jenkins Exploit

![1616384755_605812f3a2ae933aa2d40.png!small?1616384755898](https://image.3001.net/images/20210322/1616384755_605812f3a2ae933aa2d40.png!small?1616384755898)

图 22. CVE_2018_1000861 Exploit

### CVE-2019-0193

CVE-2019-0193是一个存在于Apache
solr搜索引擎中的命令执行漏洞。solr默认端口号为8983。攻击者可利用dataConfig参数构造恶意请求，实现远程代码执行。

![1616384760_605812f89651dc0ee71d7.png!small?1616384760840](https://image.3001.net/images/20210322/1616384760_605812f89651dc0ee71d7.png!small?1616384760840)

图 23. CVE_2019_0193 Exploit

其中，sysrv003通过hello_src_exp_Solr模块调用hello_src_exp_cve_2019_0193模块。sysrv007中，移除了hello_src_exp_Solr模块，仅剩hello_exp_CVE_2019_0193模块代替之。

### CVE-2020-14882

WebLogic默认端口号为7001。未经身份验证的远程攻击者可以通过构造特殊的HTTP GET请求，利用该漏洞在受影响的WebLogic
Server上执行任意代码

![1616384764_605812fce0e2f1c3f040d.png!small?1616384765318](https://image.3001.net/images/20210322/1616384764_605812fce0e2f1c3f040d.png!small?1616384765318)

图 24. CVE_2020_14882 漏洞检测

![1616384767_605812ffd41d651f5dc8f.png!small?1616384768328](https://image.3001.net/images/20210322/1616384767_605812ffd41d651f5dc8f.png!small?1616384768328)

图 25. CVE_2020_14882 Exploit

其中，sysrv007移除了hello_src_exp_Weblogic模块，以hello_exp_CVE_2020_14882模块代替之。

### Hadoop未授权访问漏洞

Hadoop YARN提供的REST API允许用户进行应用创建、任务提交执行等操作，默认端口号8088。配置不当将导致未授权访问漏洞。

![1616384772_60581304a41d779606bc0.png!small?1616384773115](https://image.3001.net/images/20210322/1616384772_60581304a41d779606bc0.png!small?1616384773115)

图 26. HadoopUnauth 漏洞检测

### ThinkPHP5 RCE

由于ThinkPHP 5框架对控制器名没有足够的检查，导致了在未开启强制路由情况下，攻击者可执行任意代码。

![1616384776_60581308886d1b0d4c486.png!small?1616384776829](https://image.3001.net/images/20210322/1616384776_60581308886d1b0d4c486.png!small?1616384776829)

图 27. ThinkPhp5Rce Exploit

### XXL-JOB未授权访问漏洞

XXL-JOB默认端口号为8080。XXL-JOB的Restful API接口没有配置认证措施，致使未授权的攻击者可构造恶意请求，造成远程代码执行。

![1616384781_6058130d3d4e01448a0cb.png!small](https://image.3001.net/images/20210322/1616384781_6058130d3d4e01448a0cb.png!small)

图 28. XxlJobUnauth Exploit

### CVE-2017-11610

CVE-2017-11610是一个存在于[Supervisor](http://supervisord.org/)d的命令执行漏洞。[Supervisor](http://supervisord.org/)d是基于Python的进程管理工具，端口号9001。通过POST恶意数据至Supervisord管理界面，可以获取服务器操作权限。

![1616384788_60581314244c6784bc5d6.png!small?1616384788379](https://image.3001.net/images/20210322/1616384788_60581314244c6784bc5d6.png!small?1616384788379)

图 29. CVE_2017_11610 Exploit

### CVE-2019-10758

Mongo-express是MongoDB的数据库管理工具。攻击者通过弱密码进入目标服务器后，可执行任意node.js代码。

下图为sysrv007构造请求用以进行漏洞利用。

![1616384793_60581319720a5d29f39a5.png!small?1616384793772](https://image.3001.net/images/20210322/1616384793_60581319720a5d29f39a5.png!small?1616384793772)

图 30. CVE_2017_11610 Exploit 1

sysrv007构造的恶意数据格式如下图所示。

![1616384797_6058131d89dd8b315d103.png!small?1616384797834](https://image.3001.net/images/20210322/1616384797_6058131d89dd8b315d103.png!small?1616384797834)

图 31. CVE_2017_11610 Exploit 2

### CVE-2020-16846

SaltStack Salt中的API存在操作系统命令注入漏洞，该漏洞允许攻击者绕过限制，以提升其特权。

sysrv007构造的恶意数据格式如下图所示。

![1616384801_6058132153c170b728691.png!small?1616384801549](https://image.3001.net/images/20210322/1616384801_6058132153c170b728691.png!small?1616384801549)

图 32. CVE_2020_16846 Exploit 1

下图为sysrv007构造请求用以进行漏洞利用。

![1616384804_60581324e20626cf31a2e.png!small?1616384805312](https://image.3001.net/images/20210322/1616384804_60581324e20626cf31a2e.png!small?1616384805312)

图 33. CVE_2020_16846 Exploit 2

### CVE-2021-3129

Ignition for Laravel 2.5.2之前版本存在授权问题漏洞，该漏洞源于程序未进行正确的身份验证，攻击者可利用该漏洞执行任意代码。

![1616384808_60581328a6af97ac52bc3.png!small?1616384808972](https://image.3001.net/images/20210322/1616384808_60581328a6af97ac52bc3.png!small?1616384808972)

图 34. hello_exp_CVE_2021_3129

下图为sysrv007构造请求用以进行漏洞利用。

![1616384812_6058132c704fe59225724.png!small?1616384812755](https://image.3001.net/images/20210322/1616384812_6058132c704fe59225724.png!small?1616384812755)

图 35. CVE_2021_3129 Exploit 1

构造的恶意数据格式如下图所示。

![1616384815_6058132fd95de504c8bb6.png!small?1616384816203](https://image.3001.net/images/20210322/1616384815_6058132fd95de504c8bb6.png!small?1616384816203)

图 36. CVE_2021_3129 Exploit 2

# 安全建议

奇安信安全能力中心提出以下安全建议：

> 1.增加服务器密码强度，定期更换密码
>
> 2.及时更新系统补丁，服务器中间件补丁，修复高危系统漏洞
>
> 3.部署安全防护产品( **奇安信天擎** ），可有效阻断此类攻击

# IoCs

 **MD5**  
  
---  
  
441874339538e7cf7ab16b87ab76623b  
  
4d7132e04d5de5dbb7e513e0c9bf77bb  
  
 **URL**  
  
---  
  
hxxp://194.40.243.98/ldr.ps1  
  
hxxp://31.210.20.120/sysrv.exe  
  
 **IP**  
  
---  
  
194.40.243.98  
  
31.210.20.120  
  
 **矿池 &钱包**  
  
---  
  
xmr-eu1.nanopool.org:14444  
  
xmr.f2pool.com:13531  
  
49dnvYkWkZNPrDj3KF8fR1BHLBfiVArU6Hu61N9gtrZWgbRptntwht5JUrXX1ZeofwPwC6fXNxPZfGjNEChXttwWE3WGURa

