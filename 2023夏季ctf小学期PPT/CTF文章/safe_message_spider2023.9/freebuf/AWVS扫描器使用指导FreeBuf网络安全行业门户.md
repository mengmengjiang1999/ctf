## 1.1是什么扫描器

Acunetix是全球排名前三的漏洞发现厂商，Acunetix Web Vulnerability
Scanner（简称AWVS）是一款知名的Web网络漏洞扫描器，其被广泛赞誉为包括最先进的SQL注入和XSS黑盒扫描技术。它能够自动爬行网站，并执行黑盒和灰盒测试技术，能够发现危险的漏洞。AWVS能够针对SQL注入、XSS、XXE、SSRF、主机头注入以及4500多个其他web漏洞执行精确的测试，并通过内置的Web管理页面轻松完成管理工作，同时能够生成非常完善的渗透报告。它包含有收费和免费两种版本，AWVS官方网站是：<http://www.acunetix.com/>。简单说AWVS是一种功能强大的Web应用程序安全扫描器，帮助用户发现可能的安全漏洞并提供修复建议。

## 1.2 怎么安装使用

### 1.2.1 安装

安装其实很简单，以windows上安装AWVS11版本为例子（Linux版本安装参考https://blog.51cto.com/lyshark/6640362），具体步骤如下：

双击exe安装包；点击“Next"；![](https://image.3001.net/images/20230826/1693035852_64e9ad4c6ac21049906ea.png!small)

选择我同意；![](https://image.3001.net/images/20230826/1693035880_64e9ad681cc544b45c8c6.png!small)

  

设置用户名和密码；

这里用户名是以邮箱为准的，密码英文数字加特殊字符，不然会提示密码太简单等问题。![](https://image.3001.net/images/20230826/1693035898_64e9ad7ae97d76325d251.png!small)

AWVS Web漏洞扫描工具地址是：https://localhost:3443/，默认端口是3443，这个可以改，具体看你自己。

![](https://image.3001.net/images/20230826/1693035917_64e9ad8d1e92ffff89981.png!small)

  

点击install开始安装![](https://image.3001.net/images/20230826/1693035938_64e9ada24eaaec2956600.png!small)

安装证书：

![](https://image.3001.net/images/20230826/1693035962_64e9adbaa7fe4791f88a7.png!small)

安全完成后打开<https://localhost:3443/>访问AWVS界面。

### 1.2.2 使用介绍：

（1）Dashboard功能：仪表盘（监视器），可以查看扫描总体结果和扫描完成目标，并且可以单独点击进去查看详细的扫描信息和漏洞信息；![](https://image.3001.net/images/20230826/1693035987_64e9add374df1e81865fb.png!small)

（2）Targets功能：可以添加扫描目标，对目标任务进行配置，配置保存可以启动扫描；![](https://image.3001.net/images/20230826/1693036002_64e9ade23f2ab89c0ee76.png!small)

（3）Vulnerabilities功能：漏洞展示，查看漏洞详情，对扫描出来的漏洞从高危到低位降序排列；

![](https://image.3001.net/images/20230826/1693036020_64e9adf4eeb84b7c8ebb4.png!small)  

（4）Scans功能：对目标进行扫描，可以修改配置扫描的参数，可以启停扫描任务，可以直接看到扫描记录；

![](https://image.3001.net/images/20230826/1693036033_64e9ae01c9013a16e4128.png!small)

  

（5）Reports功能：可以对扫描的漏洞报告、扫描任务报告和目标报告进行查看导出；![](https://image.3001.net/images/20230826/1693036045_64e9ae0dec4c065300577.png!small)

  

（6）Setting功能:可以对Awvs进行设置，有包含一些地址和组织的功能需要自己手动添加，也有排除一些地址和组织的功能，需要自己手动添加；

![](https://image.3001.net/images/20230826/1693036057_64e9ae19ac3c86bf1bec4.png!small)  

### 1.2.3 创建一个扫描任务

  1. 在“Target”页签选择“Add Target”填入扫描目标地址  

![](https://image.3001.net/images/20230826/1693036117_64e9ae552a25cd6671d12.png!small)

![](https://image.3001.net/images/20230826/1693036129_64e9ae61c150f04664f3d.png!small)

  

  2. 设置扫描选项，包括

  * 扫描业务关键性（低，正常，高，关键）：可以根据中共筛选扫描关键漏洞。
  * 扫描速度：快速（默认）——10个并发请求，无限制。中等——5个并发请求，每20ms发送一次请求。慢——2个并发请求，每50ms发送一次请求。较慢——1个并发请求，每120ms发送一次请求。
  * 连续扫描开关：每天快速扫描一次目标并更新最新的漏洞。连续扫描每周执行一次完整扫描。
  * 站点登录：可以选择自动登录，多数情况下扫描器自动识别登录链接，但需要用户提供站点用户名和密码。也可以选择登录序列记录器记录登录序列（*.lsr文件），然后保存上传，这种登录方式可以针对例如验证码或其他多因子复杂登录场景。
  * AcuSensor：AcuSensor允许扫描器从PHP、.NET或Java web应用程序中收集更多信息，从而改进扫描结果并减少误报。在运行web扫描之前，下载并安装此目标的AcuSensor。

![](https://image.3001.net/images/20230826/1693036207_64e9aeaf48baed6d90bec.png!small)

  * 其他高级选项：（1）页面爬虫，扫描目标要排查的路径，一般把用户注销排除。爬网程序在启动时要导入的文件。接受的格式包括带有URL列表的文本文件、WVS Sniffer日志、Fiddler SAZ、Selenium脚本、BURP保存的状态文件或HAR文件。（2）HTTP配置：配置http认证和代理。（3）高级配置：可以设置强制Acunetix使用所选技术的设置扫描网站；可以自定义请求头；可以配置执行时间和问题跟踪器等。

![](https://image.3001.net/images/20230826/1693036221_64e9aebdbaf8ecdc6d862.png!small)

  

  3. 保存target,并执行扫描任务跳转到Scan页签。  

![](https://image.3001.net/images/20230826/1693036256_64e9aee09e2749423560d.png!small)  

扫描完成可以生存扫描报告，跳转到Report页签，报告生成就可以点击download下载报告。

  

