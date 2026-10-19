![](https://image.3001.net/images/20211128/1638093919_61a3545fd2a2fbbb9fec0.png!small)

## 关于Scrummage

Scrummage是一款功能强大的OSINT和威胁情报框架，并且整合了以下两个框架中的优秀特性：

  * [ _Scumblr_](https://github.com/Netflix-Skunkworks/Scumblr)项目；
  * [ _OSINT Framework_](https://osintframework.com/)项目：一个可视化工具，引入了一系列可用于搜索各种内容的站点；

该工具中提供了大量的功能插件，这也是Scrummage的独特之处，其中提供的Python/Flask
web应用程序只是一个简单、轻量级的应用程序，支持广大用户根据自己的需求轻松进行功能扩展，并为用户提供管理大型结果池的能力。除此之外，安装过程简单方便也是该工具的一个主要优点。

## Scrummage插件列表

  * Blockchain Search
  * Domain Fuzzer
  * Twitter Scraper
  * Instagram Search
  * Have I Been Pwned Search
  * Ahmia Darkweb Search
  * IP Stack Search
  * Threat Crowd Search
  * Yandex and Naver Search
  * Vkontakte Search
  * Vulners Search
  * Built With Search
  * You*Tube Search
  * ...

## 工具安装

当前版本的Scrummage支持Debian、RHEL和基于SUSE的Linux发行版系统。建议广大用户在Ubuntu
18.4或更高版本系统上使用Scrummage，其中Ubuntu 20.04最为理想。

首先， 将项目代码克隆至你想要运行Web应用程序的本地路径：

    
    
    user@linux:~$ git clone https://github.com/matamorphosis/Scrummage

在命令行终端中切换至项目根目录：

    
    
    user@linux:~$ cd Scrummage/installation

使用root权限运行install.sh
Bash脚本来安装该工具所需的依赖组件，如果你想要修改默认的用户名和数据库，可以按照下列方式修改“install.sh”脚本中的对应内容：

    
    
    DATABASE="scrummage"  
    
    USER="scrummage"  

如需修改开发环境或生产环境，可以修改“install.sh”脚本中的对应内容：

    
    
    FLASK_ENVIRONMENT="development"

接下来，运行下列命令来完成工具的配置和安装：

    
    
    user@linux:/<PATH-TO-SCRUMMAGE>/installation$ sudo bash install.sh

安装完成后，工具会打印出用户名和数据库信息，并创建一个随机密码。如果你想要创建新用户，可以使用“Create_User.py”脚本：

    
    
    user@linux:/<PATH-TO-SCRUMMAGE>/installation$ python3 Create_User.py --username/-u Username --password/-p Password --admin/-a [True | False] --blocked/-b [True | False]

如果你想使用自己的证书，而不想使用默认的自签名证书，请将证书的.crt和.key文件拷贝到项目的/certs目录中。

接下来，导航至“/app/plugins/common/config”，验证Web应用信息之后，确保证书配置正确。然后应用配置文件：

    
    
    user@linux:/<PATH-TO-SCRUMMAGE>/app/plugins/common/config$ [vim/emacs/nano/gedit/leafpad] config.json
    
    
    "web_app": {
    
      "debug": false,
    
      "host": "127.0.0.1",
    
      "port": 5000,
    
      "certificate_file": "../certs/certificate.crt",
    
      "key_file": "../certs/privateKey.key",
    
      "api_secret": "",
    
      "api_validity_minutes": 60,
    
      "api_max_calls": 10,
    
      "api_period_in_seconds": 60
    
    },

确保Chrome和Chromedriver路径正确：

    
    
    "google_chrome": {
    
      "application_path": "/usr/bin/google-chrome",
    
      "chromedriver_path": "/usr/bin/chromedriver"
    
    },

如果你想使用代理，你需要在“proxy”设置中配置，并将“use_system_proxy”设置为“true”：

    
    
    "proxy": {
    
      "http": "",
    
      "https": "",
    
      "use_system_proxy": false
    
    },

如果你想添加组织相关的信息，可以设置下列内容：

    
    
    "organisation": {
    
      "name": "",
    
      "website": "",
    
      "domain": "",
    
      "subdomains": []
    
    },

最后一步，导航至项目根目录下，然后启动服务器（用户名和密码在之前的步骤中均已提供）：

    
    
    user@linux:~$ cd /<PATH-TO-SCRUMMAGE>/app
    
    user@linux:/<PATH-TO-SCRUMMAGE>/app$ python3 Scrummage.py

## 工具使用截图

### 工具仪表盘

![](https://image.3001.net/images/20211128/1638094258_61a355b27697b42cb1a29.png!small)

### 事件

![](https://image.3001.net/images/20211128/1638094264_61a355b8c30cf923f5bd7.png!small)

### 结果

![](https://image.3001.net/images/20211128/1638094273_61a355c1955777d2843b5.png!small)

![](https://image.3001.net/images/20211128/1638094279_61a355c78d316aed7049c.png!small)

###
任务![](https://image.3001.net/images/20211128/1638094292_61a355d4761a979be371f.png!small)

  
![](https://image.3001.net/images/20211128/1638094306_61a355e2346d943fd06cf.png!small)

![](https://image.3001.net/images/20211128/1638094319_61a355eff26a3bc720b76.png!small)

![](https://image.3001.net/images/20211128/1638094338_61a356027c75fec69b3af.png!small)

![](https://image.3001.net/images/20211128/1638094355_61a3561378a22dcf9022c.png!small)

### 账号设置

![](https://image.3001.net/images/20211128/1638094369_61a356210a27d505486ce.png!small)

![](https://image.3001.net/images/20211128/1638094375_61a35627cebfdcbc79369.png!small)

### 识别

![](https://image.3001.net/images/20211128/1638094384_61a35630415bdbcb1749c.png!small)

![](https://image.3001.net/images/20211128/1638094389_61a35635df900575aec1c.png!small)

![](https://image.3001.net/images/20211128/1638094396_61a3563c6c8b983e3d336.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL v3_](https://www.gnu.org/licenses/gpl-3.0)开源许可证协议。

## 项目地址

 **Scrummage：** 【[ _GitHub传送门_](https://github.com/matamorphosis/Scrummage)】

