> 文章背景：菜鸡刚刚上班，要求在centos7上跑awvs之前都是在kali上面跑的，没有经验在公司搞了一个下午没搞定。于是从周六下午搞到晚上搞定，
> 写此这文章当笔记和纪念第一次在网上写东西，大佬轻喷XD

## 1.下载awvs

<https://www.ddosi.org/awvs-3/>

强烈推荐收藏这个大佬的站点内有大量优秀文档资源

下载好后上传服务器

赋予脚本执行权限

chmod +x 脚本名

下载依赖

先使用yum安装gcc和libstdc++.so.6

yum install gcc libstdc++-4.8.5-44.el7.i686 libatk-bridge-2.0.so.0
libxkbcommon.so.0

libpango-1.0.so.0 libXcomposite.so.1 libcups.so.2 libXrandr.so.2 bzip2 -y

使用编译的方式安装GLIBC_2.18

wget下载安装包

wget <http://mirrors.ustc.edu.cn/gnu/libc/glibc-2.18.tar.gz>

解压安装包

    
    
    tar -zxvf glibc-2.18.tar.gz

开始编译

    
    
    cd glibc-2.18.tar.gz
    mkdir build
    cd build
    ../configure --prefix=/usr
    make -j 4  
    makeinstall

开始安装awvs

    
    
    ./acunetix_14.7.220425114_x64.sh

一路回车即可&YES即可

安装完成

开启防火墙的3443端口

    
    
    firewall-cmd --add-port=3443/tcp --permanent
    firewall-cmd --add-port=3443/udp --permanent

重启防火墙规则

    
    
    firewall-cmd --reload

访问<https://IP:3443>

![](https://image.3001.net/images/20220716/1657979400_62d2c2087008f0330425b.png!small)

  

显示未激活，现在开始激活破解

首先停止AWVS

    
    
    systemctl stop acunetix

进入hosts文件添加三行地址

在破解文件夹中的readme.txt文件中有写明

    
    
    vim /etc/hosts

添加以下三行地址

    
    
    127.0.0.1 updates.acunetix.com
    127.0.0.1 erp.acunetix.com
    127.0.0.1 bxss.me

将破解文件下的license_info.json和wa_data.dat文件复制粘贴到

/home/acunetix/.acunetix/data/license/目录下，直接覆盖

    
    
    cp license_info.json /home/acunetix/.acunetix/data/license/
    cp wa_data.dat /home/acunetix/.acunetix/data/license/

然后将两个文件所有者设置为root，并设为只读与不可修改文件

    
    
    chown root:root license_info.json
    chown root:root wa_data.dat
    chattr +i license_info.json
    chattr +i wa_data.dat

然后重新启动awvs服务

    
    
    systemctl start acunetix

此时激活成功，并可正常扫描

![](https://image.3001.net/images/20220716/1657979494_62d2c2669f8e6dd221422.jpg!small)

## 踩坑笔记

如果不在hosts文件写入地址，会激活成功扫码失败认证报错

如果没有安装bzip2会发生安装错误

如果没有安装GLIBC_2.18会发生服务起来了，端口没起来导致网页无法访问

如果破解没有过程中，没有停止awvs很可能会导致破解失败

以及selinux必须为关闭状态

awvs软件地址<https://www.ddosi.org/awvs-3/>

非常感谢雨苁大佬分享的资源和安装教程

如果侵权告知就删

