# docker搭建wooyun 8.8w漏洞库

![1601083819_5f6e99abc52337d2f7be6.jpg!small](https://image.3001.net/images/20200926/1601083819_5f6e99abc52337d2f7be6.jpg!small)

>
> 最近迷上了docker，其轻量化、易移植性深得我喜爱。然后就像在本地搭个docker版wooyun用于学习挖洞知识，于是在网站找了一圈，只有VM版，docker
> hub找了下载下来却发现并不是wooyun漏洞库，而是漏洞靶场。于是为了方便自己以后使用也补全网上缺少这种版本的空缺，着手开搞！

## 环境搭建（centos7、apache、mariadb、php）

采用[LNMP一键安装包](https://lnmp.org/)无人值守方式搭建

    
    
    # 安装lamp
    wget http://soft.vpser.net/lnmp/lnmp1.7.tar.gz -cO lnmp1.7.tar.gz;\
    tar zxf lnmp1.7.tar.gz && cd lnmp1.7;\
    # lnmp脚本无人值守命令解释：DBSelect="6"表示MariaDB 5.5、PHPSelect="5"表示PHP5.6、SelectMalloc="1"表示不安装内存分配器、ApacheSelect="1"表示Apache2.2，其他请查看https://lnmp.org/faq/v1-5-auto-install.html
    LNMP_Auto="y" DBSelect="6" DB_Root_Password="${DB_Root_Password}" InstallInnodb="y" PHPSelect="5" SelectMalloc="1" ApacheSelect="1" ServerAdmin="" ./install.sh lamp;
    

> 这个地方踩了个大坑，当lnmp无人值守脚本选择DB为mysql（而不是mariadb）时，会出现在安装完成后不会自动退出，会停留在completed!
> enjoy it。这样会导致Dockerfile构建失败。后面换成mariadb才会自动退出。

## 源码（GitHub仓库地址：<https://github.com/V7hinc/wooyun_final>）

>
> 代码主要来自于[hanc00l的wooyun_public的wooyun_final](https://github.com/hanc00l/wooyun_public)漏洞信息来自于[m0l1ce的wooyun_all_bugs_8.8W](https://github.com/m0l1ce/wooyunallbugs)，包含8.8W漏洞信息（不含知识库）

  * 支持多关键字搜索和在漏洞详情中搜索
  * 漏洞详情图片支持相对路径读取本地图片
  * 代码适应PHP5.6

代码主要从hanc00l的wooyun_final代码做了以下改动

    
    
    1、更改bug_detail.php图片路径为相对路径，可以正常读取本地图片，而不用去查在线图片
    <hr align="center"/<?php echo str_replace('http://static.loner.fm/','',$bug_detail['wybug_detail']);?>
    
    2、增加picture目录和图标
    3、增加upload和部分图片
    

源码需在lamp环境下运行，拉取[源码](https://github.com/V7hinc/wooyun_final)到网站根目录，下载[wooyun数据库wooyun_bugs_db.tar.bz2](https://github.com/V7hinc/wooyun_final/releases/tag/1.0)文件解压到MySQL文件路径下wooyun文件夹

## Docker搭建wooyun

Dockerfile文件
[传送门](https://github.com/V7hinc/wooyun_final/blob/master/Dockerfile)

Dockerfile构建方法

    
    
    docker build -t v7hinc/wooyun github.com/V7hinc/wooyun_final
    

或者直接拉取已经生成的docker镜像

    
    
    docker pull v7hinc/wooyun
    

创建新的容器

> 由于wooyun的图片占容量较大，所以在Dockerfile中加了VOLUME挂载卷，不至于把容器撑的很大

2种挂载方法（这个地方容易有坑）

> 1、不指定宿主机挂载目录
    
    
    docker run --name wooyun -p 5000:80 -dit v7hinc/wooyun:latest /bin/bash
    # 创建好容器后查看挂载位置，cd进入查询结果"Source"后面的路径,就是对应容器中upload的路径
    [root@localhost ~]# docker inspect wooyun | grep "Source"
                    "Source": "/var/lib/docker/volumes/21313d9e09fd3b571ae1daab856d07012f2081c940a9d839c121fa62f7f43764/_data",
    

> 2、指定宿主机挂载目录
    
    
    docker run --privileged=true --name wooyun -v ~/upload:/home/wwwroot/default/upload -p 5000:80 -dit v7hinc/wooyun:latest /bin/bash
    

> 到此wooyun漏洞库已经还原好了。可以通过访问[http://IP:5000](http://ip:5000/)访问到了
> 但是会发现打开漏洞详情图片看不了
> 接下来需要下载图片资源，然后解压到docker宿主机的~/upload目录下就可以看到图片了，如果是采用不指定宿主机挂载目录则解压到"Source"对应的路径即可

百度网盘下载链接: <https://pan.baidu.com/s/1cadRdAC5Cxb1M_o5URNXSw>提取码: tkqg

（如果下载链接失效可前往项目仓库，项目仓库内容将会根据需要不定期更新）

效果图 Nice：

![index](https://image.3001.net/images/20200925/1601047267_5f6e0ae3a3fcb578d6282.png!small)

![bug_detail](https://image.3001.net/images/20200925/1601047310_5f6e0b0e53d80bee5371d.png!small)

#### 容器内相关软件安装目录

    
    
    Apache目录：/usr/local/apache/
    MariaDB 目录 : /usr/local/mariadb/
    MariaDB数据库所在目录：/usr/local/mariadb/var/
    PHP目录 : /usr/local/php/
    默认网站目录 : /home/wwwroot/default/
    

#### 容器内相关配置文件位置

    
    
    Apache配置文件：/usr/local/apache/conf/httpd.conf
    Apache虚拟主机配置文件目录：/usr/local/apache/conf/vhost/
    Apache默认虚拟主机配置文件：/usr/local/apache/conf/extra/httpd-vhosts.conf
    虚拟主机配置文件名称：/usr/local/apache/conf/vhost/域名.conf
    MySQL配置文件：/etc/my.cnf
    PHP配置文件：/usr/local/php/etc/php.ini
    php-fpm配置文件：/usr/local/php/etc/php-fpm.conf
    

# 其它

  * 本程序只用于技术研究和个人使用，程序组件均为开源程序，漏洞和知识库来源于乌云公开漏洞，版权归wooyun.org。

项目仓库地址：<https://github.com/V7hinc/wooyun_final>

