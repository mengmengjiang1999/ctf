## 0x00 简介

Laravel是一套简洁、优雅的PHP Web开发框架(PHP Web
Framework)，旨在实现的Web软件的MVC架构，它可以让开发者从面条一样杂乱的代码中解脱出来，帮助构建一个完美的网络APP，而且每行代码都可以简洁、富于表达力。

在Laravel中已经具有了一套高级的PHP ActiveRecord实现 -- Eloquent
ORM。它能方便的将“约束（constraints）”应用到关系的双方，这样开发者就具有了对数据的完全控制，而且享受到ActiveRecord的所有便利。Eloquent原生支持Fluent中查询构造器（query-builder）的所有方法。

## 0x01 漏洞概述

Laravel <= 8.4.2
存在远程代码执行漏洞，当Laravel开启了Debug模式时，由于Laravel自带的2.5.2之前的Ignition功能的某些接口和函数存在过滤不严，未经过身份验证的远程攻击者可以发起恶意请求，通过构造恶意Log文件等方式触发phar反序列化，从而造成远程代码执行，控制服务器。

## 0x02 影响版本

    
    
    Laravel<=8.4.2  
    Ignition<2.5.2

## 0x03 环境搭建

1.使用github已经搭建好的环境进行复现。

    
    
    gitclone git://github.com/SNCKER/CVE-2021-3129

![image-20210701004921987](https://image.3001.net/images/20210713/1626108284_60ec717c16c3b3e4bdad1.png!small)

2.切换到刚刚下载的目录，执行以下命令即可自动完成环境搭建和启动。

    
    
    docker-compose up -d

![image-20210701004951943](https://image.3001.net/images/20210713/1626108286_60ec717e292647815bf74.png!small)

3.浏览器访问 <http://192.168.141.131:8888>，出现如下界面。

![image-20210701005008752](https://image.3001.net/images/20210713/1626108287_60ec717fac06c8d2e3778.png!small)

点击Generate app key，发送请求，在配置文件中配置了一个加密key。

![image-20210701005023999](https://image.3001.net/images/20210713/1626108288_60ec7180ad4dc9a5876f6.png!small)

再刷新一下界面，出现以下内容即搭建成功。

![image-20210701005039118](https://image.3001.net/images/20210713/1626108289_60ec7181c8fdf86943d47.png!small)

## 0x04 漏洞复现

1.github上的环境附带exp，使用vim打开查看，其默认目标为本地，执行"cat /etc/passwd"命令

![image-20210701005132651](https://image.3001.net/images/20210713/1626108291_60ec71831a753b2e4d794.png!small)

![image-20210701005208538](https://image.3001.net/images/20210713/1626108292_60ec718485c4aadbdace1.png!small)

2.在执行exp之前，需要下载phpggc工具，phpggc要和exploit.py在放同一文件夹内

    
    
    gitclone git://github.com/ambionics/phpggc.git

![image-20210701005227914](https://image.3001.net/images/20210713/1626108294_60ec71866bcae516a742b.png!small)

3.执行如下代码，即可默认查看 /etc/passwd 文件

    
    
    python3 exploit.py

![image-20210701005253283](https://image.3001.net/images/20210713/1626108296_60ec7188eeef226e57de9.png!small)

4.简单修改一下 exploit.py 脚本即可执行任意命令

Vim打开脚本，首先在exploit.py开头import sys库

![image-20210701005314378](https://image.3001.net/images/20210713/1626108299_60ec718bcf7416198062e.png!small)

主函数改为如下内容（注意缩进）

    
    
    args= sys.argv  
    url= args[1]  
    command= args[2]  
    Exp(url, command)

![image-20210701005355050](https://image.3001.net/images/20210713/1626108302_60ec718e159130e3114ea.png!small)

运行如下指令，第1个参数即为目标ip，第2个参数即为想要执行的命令

    
    
    python3 exploit.py http://127.0.0.1:8888 'ifconfig'

![image-20210701005535618](https://image.3001.net/images/20210713/1626108304_60ec719059fb5d6f99c5f.png!small)

## 0x05 防护建议

1.使用白名单限制相关web项目的访问来降低风险；

2.将 Laravel 框架升级至8.4.3及其以上版本，或者将facade ignition组件升级至 2.5.2 及其以上版本。

