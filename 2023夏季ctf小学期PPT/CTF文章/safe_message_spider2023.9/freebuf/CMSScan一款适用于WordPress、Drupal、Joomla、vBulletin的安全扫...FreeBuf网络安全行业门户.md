## 前言

**今天给大家介绍的是一款名叫CMSScan的针对内容管理系统的安全扫描工具，各位安全研究人员可以使用CMSScan来检测WordPress、Drupal、Joomla和vBulletin网站的安全问题。**

![1.png](https://image.3001.net/images/20181123/1542962601_5bf7bda947e25.png!small)

## CMSScan

CMSScan提供了一种中心化的安全扫描仪表盘，广大研究人员可以直接在这个仪表盘上直接进行内容管理系统的安全扫描操作。CMSScan整合了多种安全扫描工具，其中包括wpscan、droopescan、vbscan和joomscan在内。它支持手动扫描和计划任务扫描，并且能够直接通过电子邮件的形式将扫描报告发送给研究人员。

## 工具安装

### 依赖组件：ruby、ruby-dev、gem、Python 3.6+和git；

    
    
    git clone <https://github.com/ajinabraham/CMSScan.git>
    
    cd CMSScan
    
    ./setup.sh

## 工具运行

    
    
    ./run.sh

### 定期扫描

CMSScan支持我们对目标内容管理系统执行定期扫描任务，但是你必须单独运行一台CMSScan服务器，并在运行scheduler.py脚本之前完成如下配置：

    
    
    #SMTP SETTINGS
    
    SMTP_SERVER= ''
    
    FROM_EMAIL= ''
    
    TO_EMAIL= ''
    
     
    
    #SERVER SETTINGS
    
    SERVER= ''
    
     
    
    #SCAN SITES
    
    WORDPRESS_SITES= []
    
    DRUPAL_SITES= []
    
    JOOMLA_SITES= []
    
    VBULLETIN_SITES= []

添加一个cronjob：

    
    
    crontab -e
    
    @weekly/usr/bin/python3 scheduler.py

## Docker

### 本地安装&构建：

    
    
    docker build -t cmsscan .
    
    docker run -it -p 7070:7070 cmsscan

### 预构建镜像：

    
    
    docker pull opensecurity/cmsscan
    
    docker run -it -p 7070:7070 opensecurity/cmsscan

## 工具运行截图

![工具运行截图](https://image.3001.net/images/20181123/1542962727_5bf7be27921a2.png!small)![工具运行截图](https://image.3001.net/images/20181123/1542962727_5bf7be273accd.png!small)

## 项目地址

> CMSScan：【[GitHub传送门](https://github.com/ajinabraham/CMSScan)】

***参考来源：[CMSScan](https://github.com/ajinabraham/CMSScan)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

