前几篇文章中讲解了如何搭建 docker 和 Java Web 环境的方法，本篇文章来教大家搭建一个好的 PHP 和 Python 环境，可以帮助开发和运行
PHP 和 Python 应用程序，使其更加高效和稳定。

## 一、 PHP 环境介绍

好的开发环境无疑会大大提升编码效率，近日钻研了一下 Python 环境安装的问题，稍加总结分享一下。本文以轻量云主机（CenTOS 7.6
系统）为例，介绍如何搭建 PHP 环境。

### 1.1、前置准备

正式开始部署前，您需完成如下的准备工作：

  1. 开通京东云账户，若您还未注册京东云账号，可在京东云官网进行注册；
  2. 账户开通后，需要进行实名认证；
  3. 购买一台或多台云主机或者轻量云主机产品；
  4. 登录轻量云主机，复制下面步骤中的命令进行执行操作；

### 1.2、搭建 PHP 环境

本次安装的是 PHP7，有些 linux 版本的 yum 默认是安装的 5，需要做如下更改

    
    
    rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm
    
    
    

安装 PHP

    
    
    yum -y install php72w
    
    

安装 PHP 扩展

    
    
    yum -y install php72w-common php72w-fpm php72w-opcache php72w-gd php72w-mysqlnd php72w-mbstring php72w-pecl-redis php72w-pecl-memcached php72w-devel
    
    

### 1.3、安装 Apache

安装 Apache

    
    
    yum install -y httpd
    systemctl start httpd
    
    

### 1.4、测试验证

新建 info.php 文件

    
    
    cd /var/www/html
    vi info.php
    
    

在文件中输入 下面内容，并保存文件

    
    
    <?php phpinfo(); ?>
    
    

![1684131354_6461ce1a8262a6c93a882.png!small?1684131354929](https://image.3001.net/images/20230515/1684131354_6461ce1a8262a6c93a882.png!small?1684131354929)

在浏览器中输入 [http://ip/info.php
查看效果](https://www.oschina.net/action/GoToLink?url=http%3A%2F%2Fip%2Finfo.php%25E6%259F%25A5%25E7%259C%258B%25E6%2595%2588%25E6%259E%259C)

![1684131364_6461ce240e999ad663185.png!small?1684131364709](https://image.3001.net/images/20230515/1684131364_6461ce240e999ad663185.png!small?1684131364709)

## 二、 Python 环境介绍

Python 是一种面向对象的解释型语言，可应用于各种领域，包括但不限于网站、游戏开发、机器人，人工智能，大数据等。 CentOS 系统本身默认安装有
python2.x，版本 x 根据不同系统版本有所不同，可通过 python --V 或 python --version 查看系统自带的 python
版本。  
本文以轻量云主机（CenTOS 7.6 系统）为例，介绍如何部署 python3.6 环境。

### 2.1、前置准备

正式开始部署前，您需完成如下的准备工作：

  1. 开通京东云账户，若您还未注册京东云账号，可在京东云官网进行注册；
  2. 账户开通后，需要进行实名认证；
  3. 购买一台或多台云主机或者轻量云主机产品；
  4. 登录轻量云主机，复制下面步骤中的命令进行执行操作；

### 2.2、搭建 Python3.6 环境

查看可以安装的 python3 版本

    
    
    yum -y list python3*
    
    

![1684131376_6461ce302e53164c0ca44.png!small?1684131376911](https://image.3001.net/images/20230515/1684131376_6461ce302e53164c0ca44.png!small?1684131376911)

安装 python3.6

    
    
    yum -y install python36
    
    

![1684131386_6461ce3a381d629488025.png!small?1684131387150](https://image.3001.net/images/20230515/1684131386_6461ce3a381d629488025.png!small?1684131387150)

验证 phthon3.6 是否安装成功

    
    
    python3 -V
    
    

![1684131398_6461ce46cf21e343407e0.png!small?1684131399446](https://image.3001.net/images/20230515/1684131398_6461ce46cf21e343407e0.png!small?1684131399446)

### 2.3、安装 PIP3

安装 pip3

    
    
    yum install python3-pip
    
    

![1684131409_6461ce51ddc1348df382d.png!small?1684131410752](https://image.3001.net/images/20230515/1684131409_6461ce51ddc1348df382d.png!small?1684131410752)

更新 pip3

    
    
    pip3 install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host http://pypi.tuna.tsinghua.edu.cn
    
    

修改 pip3 软件源

    
    
    sudo pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    
    

### 2.4、测试验证

测试 pip3 使用

    
    
    pip3 install lxml
    
    

![1684131421_6461ce5d8c16695fa6885.png!small?1684131422207](https://image.3001.net/images/20230515/1684131421_6461ce5d8c16695fa6885.png!small?1684131422207)

创建一个 hello.py 文件

    
    
    vi hello.py
    
    

![1684131433_6461ce69a9750bf570a3c.png!small?1684131434036](https://image.3001.net/images/20230515/1684131433_6461ce69a9750bf570a3c.png!small?1684131434036)

在文件中输入 print ("hello world") ， 并保存文件

![1684131443_6461ce73dbe4941eacda9.png!small?1684131444563](https://image.3001.net/images/20230515/1684131443_6461ce73dbe4941eacda9.png!small?1684131444563)

执行 python 脚本，输出 hello world

    
    
    python3 ./hello.py 
    
    

![1684131454_6461ce7e213d69ff6df9b.png!small?1684131454528](https://image.3001.net/images/20230515/1684131454_6461ce7e213d69ff6df9b.png!small?1684131454528)

