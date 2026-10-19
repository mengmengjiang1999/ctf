![](https://image.3001.net/images/20211126/1637911988_61a08db446fa9374b70db.jpg!small)

## 关于FUSE

FUSE是一款功能强大的渗透测试安全工具，可以帮助广大研究人员在最短的时间内迅速寻找出目标软件系统中存在的文件上传漏洞。

FUSE本质上是一个渗透测试系统，主要功能就是识别无限制可执行文件上传（UEFU）漏洞。关于UEFU无限制可执行文件上传漏洞的相关内容，可以参考这篇【[
_文章_](https://wsp-lab.github.io/papers/lee-fuse-ndss20.pdf)】，该文章发表于NDSS2020。关于如何配置和执行FUSE，请参阅以下内容。

## 工具安装

当前版本的FUSE支持在Ubuntu 18.04和Python 2.7.15环境下工作。

首先，我们需要使用下列命令安装好FUSE正常运行所需的依赖组件：

    
    
    # apt-get install rabbitmq-server
    
    # apt-get install python-pip
    
    # apt-get install git

接下来，将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/WSP-LAB/FUSE

并切换至项目目录下配置好依赖环境：

    
    
    $ cd FUSE && pip install -r requirements.txt

如果你想要使用[
_selenium_](https://selenium.dev/selenium/docs/api/py/index.html)实现无头浏览器验证的话，你还需要安装好Chrome和Firefox
Web驱动器。【[ _文档_](https://selenium.dev/selenium/docs/api/py/index.html)】

## 工具使用

### FUSE配置

FUSE使用了用户提供的[ _配置文件_](https://github.com/WSP-LAB/FUSE/blob/master/configs/default-credential.conf)来为目标PHP应用程序指定参数。在测试目标Web应用程序之前，必须将相关参数提供给脚本执行。具体请参考项目的[
_README文件_](https://github.com/WSP-LAB/FUSE/blob/master/configs/README.md)或[
_配置文件参考样例_](https://github.com/WSP-LAB/FUSE/blob/master/configs)。

 **针对文件监控器的配置样例（可选）：**

    
    
    $ vim filemonitor.py
    ...
     10 MONITOR_PATH='/var/www/html/' <- Web root of the target application
     11 MONITOR_PORT=20174            <- Default port of File Monitor
     12 EVENT_LIST_LIMITATION=8000    <- Maxium number of elements in EVENT_LIST
    ...

### FUSE执行

 **FUSE：**

    
    
    $ python framework.py [Path of configuration file]

 **文件监控器：**

    
    
    $ python filemonitor.py

 **扫描结果：**

  * 当FUSE完成了渗透测试任务之后，将会在当前工作目录下创建一个[HOST]目录和一个[HOST_report.txt]文件。
  * [HOST]文件夹中存储的是工具尝试上传的所有文件。
  * [HOST_report.txt]文件中包含了渗透测试的执行结果，以及触发了UEFU漏洞的相关文件信息。

## 漏洞CVE

如果你在号盗了UFU或UEFU漏洞，可以通过运行FUSE来获取相关漏洞的CVE编号信息：

 ** **应用程序****

|

 ** **CVE****  
  
---|---  
  
Elgg

|

CVE-2018-19172  
  
ECCube3

|

CVE-2018-18637  
  
CMSMadeSimple

|

CVE-2018-19419, CVE-2018-18574  
  
CMSimple

|

CVE-2018-19062  
  
Concrete5

|

CVE-2018-19146  
  
GetSimpleCMS

|

CVE-2018-19420, CVE-2018-19421  
  
Subrion

|

CVE-2018-19422  
  
OsCommerce2

|

CVE-2018-18572, CVE-2018-18964, CVE-2018-18965, CVE-2018-18966  
  
Monstra

|

CVE-2018-6383, CVE-2018-18694  
  
XE

|

XEVE-2019-001  
  
## 工具&论文引用

    
    
    @INPROCEEDINGS{lee:ndss:2020,
    
        author = {Taekjin Lee and Seongil Wi and Suyoung Lee and Sooel Son},
    
        title = {{FUSE}: Finding File Upload Bugs via Penetration Testing},
    
        booktitle = {Proceedings of the Network and Distributed System Security Symposium},
    
        year = 2020
    
    }

## 项目地址

 **FUSE：** 【[ _GitHub传送门_](https://github.com/WSP-LAB/FUSE)】

## 参考资料

  * [ _https://wsp-lab.github.io/papers/lee-fuse-ndss20.pdf_](https://wsp-lab.github.io/papers/lee-fuse-ndss20.pdf)
  * [ _https://selenium.dev/selenium/docs/api/py/index.html_](https://selenium.dev/selenium/docs/api/py/index.html)
  * [ _https://github.com/WSP-LAB/FUSE/blob/master/configs/default-credential.conf_](https://github.com/WSP-LAB/FUSE/blob/master/configs/default-credential.conf)
  * [ _https://github.com/WSP-LAB/FUSE/blob/master/configs_](https://github.com/WSP-LAB/FUSE/blob/master/configs)
  * [ _https://wsp-lab.github.io/﻿_](https://wsp-lab.github.io/)

