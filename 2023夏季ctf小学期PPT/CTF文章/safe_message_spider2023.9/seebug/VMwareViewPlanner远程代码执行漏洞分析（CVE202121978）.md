**作者：水泡泡@知道创宇404积极防御实验室  
日期：2021年3月5日**

### 0x01 漏洞描述

View Planner是VMware官方推出的一款针对view桌面的测试工具，通过这个测试工具可以估算出在指定的应用环境下可以发布多少个view桌面。

View Planner 的logupload端点缺乏输入验证，导致具有查看View Planner
Harness网络访问权限的未经授权的攻击者可以上载和执行精心编制的文件，从而导致在logupload容器中执行远程代码。

影响范围：VMware View Planner <=4.6.0

### 0x02 环境安装

下载镜像：

[https://my.vmware.com/group/vmware/downloads/details?downloadGroup=VIEW-PLAN-460&productId=1067&rPId=53394](https://my.vmware.com/group/vmware/downloads/details?downloadGroup=VIEW-PLAN-460&productId=1067&rPId=53394) （选择View Planner Harness ）

![](https://images.seebug.org/content/images/2021/03/f5bca957-76ba-4621-98d6-a6c8a5fc0edf.png-w331s)

下载需要注册一个账号且下载需要审核，需要等待一段时间，这里分享我已经下载好的：

链接: <https://pan.baidu.com/s/1aeNW1HUyCkZze1bs7vplzg>  
提取码: vv42

使用VMware直接加载ova文件，安装过程中按照提示初始化 ssh root账号的初始密码，成功搭建。

![](https://images.seebug.org/content/images/2021/03/a7c9f85a-cb19-44fd-b0ea-7deee7041bc8.png-w331s)

### 0x03 漏洞复现

按照twitter上公开的POC，向logupload端点构造请求包（路径使用相对路径即可）。

![](https://images.seebug.org/content/images/2021/03/4d6d4106-ba3a-4e12-92b2-4d87fe6ca80e.png-w331s)

其中上传的文件内容是`log_upload_wsgi.py`的源文件，但添加了执行命令的代码，在上传成功之后，再请求一次logupload端点，收到curl请求，命令执行成功。

![](https://images.seebug.org/content/images/2021/03/6b5653d0-3e62-425a-b1b7-7fa7a1fcabd6.png-w331s)

至此漏洞复现成功。

### 0x04漏洞分析

在分析之前，先简单讲一下View Planner的部署架构。

View Planner
的web服务由docker搭建提供，其中80，443端口的内容由appacheServer容器提供，而8081由crossbar容器提供，为ws服务，主要处理登陆后的后端交互逻辑。

![](https://images.seebug.org/content/images/2021/03/caabae8a-4d3a-411f-b07c-d0d99f20d90f.png-w331s)

ssh 到 viewplanner虚拟机，scp将`/root/viewplanner` 源码拉出来，全局搜索logupload。

![](https://images.seebug.org/content/images/2021/03/836a5197-49b8-4694-8792-c68e26432861.png-w331s)

可以看到apache
配置文件配置了logupload端点的指向文件为`/etc/httpd/html/wsgi_log_upload/log_upload_wsgi.py`

其路径`/etc/httpd/html/` 实际是容器内的路径，对应宿主机的`/root/viewplanner/httpd`

![](https://images.seebug.org/content/images/2021/03/58ae1e5c-3df4-4357-b1c2-4c512fa25505.png-w331s)

定位到`/root/viewplanner/httpd/wsgi_log_upload/log_upload_wsgi.py` 文件。

![](https://images.seebug.org/content/images/2021/03/0e228a1d-47b1-48e7-be5f-a7dce062eaf5.png-w331s)

代码很简单，从cgi中获取`logfile`
和`logMetaData`两个参数数据，如果`logMetaData`参数传入了`json`数据，则从`json`数据中获取`itrLogPath`和`logFileType`两个键值，随之将`itrLogPath`和`logFileType`与`resultBasePath`
进行路径拼接，判断路径是否存在，不存在则创建，

之后判断`logfile`是否为上传文件，上传了文件，如果`logFileType`参数的值不等于`workloadLogsZipFile`
则直接将`resultBasePath`，`itrLogPath`，`logFileType`三个参数的值进行路径拼接，并进行文件写入。

由于缺少路径规范过滤，只需要稍微构造一下数据包即可上传恶意文件到任意路径，从而可以覆盖`log_upload_wsgi.py`
文件，达到远程代码执行的效果。

### 0x05 补丁分析

至此漏洞分析完毕，下载官方补丁进行对比分析（左补丁）：

![](https://images.seebug.org/content/images/2021/03/bd13433e-3c98-4c83-b040-7119e1998a8e.png-w331s)

加入了个password参数也就是使用`loguplaod`这个端点需要密码才可以访问，但取的`secret_key`来自于`wsgi.config`，硬编码值为：`vmware-viewplanner-ca$hc0w`，有点掩耳盗铃的味道；

不过后面代码，对拼接后的路径使用normpath进行路径规范化，并用`startswith`限制写入的文件必须在
`/etc/httpd/html/vpresults`目录下，也就没法再跨路径上传文件，至此此漏洞算是修复完成了。

### 0x06 总结

此系统暴露在外网的IP非常少，大多数在内网，漏洞简单但危害严重，建议广大管理员赶快升级，避免在即将到来的行动中失分。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1495/>

