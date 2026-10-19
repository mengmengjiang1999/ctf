### 项目介绍：

PeTeReport（PenTest 报告）是一种开源应用程序漏洞报告工具，旨在通过简化编写和生成报告的任务来协助渗透测试/红队工作。

该工具专注于产品安全，可帮助安全研究人员和渗透测试人员提供详细的调查结果、附录、攻击路径并管理调查结果模板数据库，以避免在报告阶段浪费时间。

PeTeReport（PenTest 报告）是用 Django 和 Python 3 编写的，旨在帮助渗透测试人员管理查找存储库、编写报告（在
Markdown 中）并生成不同格式（HTML、CSV、PDF、Jupyter 和 Markdown）的报告。

### 项目地址

<https://github.com/1modm/petereport>

### 项目文档

https://1modm.github.io/petereport/

### 项目安装

前提：

安装docker及docker-compose（建议安装1.26.1， 如果版本过高如1.29可能会报错）

    
    
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun  
    curl -L "https://github.com/docker/compose/releases/download/1.26.1/docker-compose-$(uname -s)-$(uname -m)" > docker-compose

1、

    
    
    git clone https://github.com/1modm/petereport.git
    

![1637769601_619e61811d6014e4d9eac.png!small?1637769600215](https://image.3001.net/images/20211125/1637769601_619e61811d6014e4d9eac.png!small?1637769600215)

2、

    
    
    docker-compose up --build

![1637856935_619fb6a73228f5be9a8ae.png!small?1637856934685](https://image.3001.net/images/20211126/1637856935_619fb6a73228f5be9a8ae.png!small?1637856934685)

安装完毕：

![1637858697_619fbd8901720d7a8badd.png!small?1637858696371](https://image.3001.net/images/20211126/1637858697_619fbd8901720d7a8badd.png!small?1637858696371)

  

  

### 项目测试

安装完毕后，生成2个账号:管理用户admin/P3t3r3p0rt 浏览用户viewer/v13w3r ,

登录界面如下：

![1637858963_619fbe934378521bb9b87.png!small?1637858962636](https://image.3001.net/images/20211126/1637858963_619fbe934378521bb9b87.png!small?1637858962636)

### 管理界面：

![1637859163_619fbf5b285d5c80cfc40.png!small?1637859162582](https://image.3001.net/images/20211126/1637859163_619fbf5b285d5c80cfc40.png!small?1637859162582)

左边有5个功能菜单，分别是dashboard(控制面板)、Configuration(配置)、Products(项目产品)、Reports(报告)、Findings(结果):

 **dashboard(控制面板):**

  

 **Configuration(配置):**

主要为用户的管理:

![1637859404_619fc04ce31b1e1b63007.png!small?1637859404316](https://image.3001.net/images/20211126/1637859404_619fc04ce31b1e1b63007.png!small?1637859404316)

 **Products(项目产品):**

主要为项目的管理，比如渗透项目/测试产品等:

![1637859476_619fc0944a41394a73d0c.png!small?1637859475672](https://image.3001.net/images/20211126/1637859476_619fc0944a41394a73d0c.png!small?1637859475672)

 **Reports(报告):**

主要为漏洞报告记录，拥有功能健全的编辑器：

![1637859580_619fc0fced44dc36708b0.png!small?1637859580509](https://image.3001.net/images/20211126/1637859580_619fc0fced44dc36708b0.png!small?1637859580509)

  

 **Findings(结果)**

里面列举了常见的弱点列表CWE:

![1637859638_619fc136dc4a1f8af8dea.png!small?1637859638334](https://image.3001.net/images/20211126/1637859638_619fc136dc4a1f8af8dea.png!small?1637859638334)

  

以及健全的结果模版：

![1637859739_619fc19ba017bb051e290.png!small?1637859739030](https://image.3001.net/images/20211126/1637859739_619fc19ba017bb051e290.png!small?1637859739030)

  

