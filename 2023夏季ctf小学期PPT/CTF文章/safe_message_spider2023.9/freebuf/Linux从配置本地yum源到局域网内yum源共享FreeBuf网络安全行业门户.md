## 一、CentOS 7.X配置本地yum源

如果CentOS服务器处在内网环境中时，如果缺少依赖包，手动安装时非常麻烦的，需要花费很多时间来寻找安装包，如果搭建了本地的yum源，就会非常方便，如果搭建了http,那么局域网内其他服务器也可以使用，搭建yum源首先需要一个centos镜像包，这里我们用得是：CentOS-7-x86_64-Everything-1908.iso

 **操作系统环境**

    
    
    CentOS Linux release 7.7.1908 (Core)
    

**配置yum源**

上传ISO镜像文件到服务器

![image.png](https://image.3001.net/images/20210430/1619772202_608bc32a6bc84474fd8e5.png!small)

挂载ISO镜像到/mnt/yum目录下(root权限执行)

    
    
    mount -t iso9660 /mnt/CentOS-7-x86_64-Everything-1908.iso /mnt/yum/
    mount: /mnt/CentOS-7-x86_64-Everything-1908.iso is write-protected, mounting read-only
    

![image.png](https://image.3001.net/images/20210430/1619772215_608bc3375c7873776564c.png!small)

将命令加入开机启动文件/etc/rc.local

    
    
    vi /etc/rc.local
    

![image.png](https://image.3001.net/images/20210430/1619772224_608bc340beeaccfbdc96a.png!small)

备份本地repo文件

    
    
    mkdir /opt/centos-yum.bak
    mv /etc/yum.repos.d/* /opt/centos-yum.bak/
    

![image.png](https://image.3001.net/images/20210430/1619772233_608bc349875843024e0a7.png!small)

创建自己的repo文件

    
    
    cd /etc/yum.repos.d/
    创建myyum.repo文件
    vi /etc/yum.repos.d/local.repo
    
    [local]
    name=local
    baseurl=file:///mnt/yum/		#本地yum源目录位置
    # enabled=1			#enabled=0配置项，表示不生效
    gpgcheck=1			
    gepkey=file:///mnt/yum/RPM-GPG-KEY-CentOS-7	#本地yum源目录位置下GPG公钥
    

![image.png](https://image.3001.net/images/20210430/1619772249_608bc35995babe6d624f0.png!small)

刷新yum缓存

    
    
    yum clean all	清除缓存
    yum makecache 	把yum源缓存到本地
    yum repolist	查看yum源信息
    yum list		列出可以通过yum源安装的包
    

![image.png](https://image.3001.net/images/20210430/1619772259_608bc363b7141ac96cf95.png!small)

**执行yum install报错注意点**

 **问题一：**

linux执行yum install报出“Loaded plugins: fastestmirror, langpacks”错误

![image.png](https://image.3001.net/images/20210430/1619772271_608bc36f0e32ba3fe773a.png!small)

 **解决方法**

1、修改配置文件

    
    
    vi /etc/yum/pluginconf.d/fastestmirror.conf
    第2行改为： enabled=0   //由 1 改成0 ，禁用该插件
    

2、修改yum源配置文件

    
    
    vi /etc/yum.conf
    第9行改为：    plugins=0  //不使用插件
    

3、清查缓存并重新加载yum源缓存

    
    
    yum clean all
    yum makecache
    

![image.png](https://image.3001.net/images/20210430/1619772285_608bc37d50a9727be297a.png!small)

**问题二：**

linux执行yum install报出“You have enabled checking of packages via GPG keys”错误

![image.png](https://image.3001.net/images/20210430/1619772292_608bc384942e045a3f472.png!small)

解决方法

1、在镜像文件挂载的文件中找到GPG公钥

    
    
    cd /mnt/yum
    

![image.png](https://image.3001.net/images/20210430/1619772300_608bc38c5034b2168c103.png!small)

2、使用rpm --import配置yum源的RPM-GPG-KEY文件

    
    
    rpm --import /mnt/yum/RPM-GPG-KEY-CentOS-7
    rpm --import /mnt/yum/RPM-GPG-KEY-CentOS-Testing-7
    

![image.png](https://image.3001.net/images/20210430/1619772307_608bc393c1dd18bbda9b4.png!small)

即可执行yum命令安装依赖包

## 二、搭建nginx服务器共享至局域网内其他主机

为了让局域网内的其他主机访问到本地的yum源，我们首先需要部署一台web服务器，比如apache或nginx等其他都可以。本次测试我们使用nginx。

 **下载nginx安装包**

nginx官网

    
    
    http://nginx.org/en/download.html
    

![image.png](https://image.3001.net/images/20210430/1619774560_608bcc60b51953b5cf643.png!small)

本次下载使用yum安装

    
    
    nginx-1.18.0.tar.gz
    

![image.png](https://image.3001.net/images/20210430/1619774572_608bcc6c4cf22928fa334.png!small)

解压

    
    
    tar -zxvf tar -zxvf nginx-1.18.0.tar.gz
    

![image.png](https://image.3001.net/images/20210430/1619774588_608bcc7c101d0ab584074.png!small)

安装运行nginx环境的依赖包

    
    
    yum -y install libtool* zlib* openssl* gcc gcc-c++ cmake pcre* libxml2*  libcurl* libjpeg* libpng libpng-devel freetype freetype-devel libxslt*
    

编译安装nginx

    
    
    cd /mnt/yum
    ./configure --prefix=/usr/local/nginx
    make && make install
    ll /usr/local/nginx/
    

![image.png](https://image.3001.net/images/20210430/1619774624_608bcca077d22dc88dce8.png!small)  
![image.png](https://image.3001.net/images/20210430/1619774639_608bccaf6abf5cc09e9ad.png!small)

创建软链接,将/mnt/yum目录映射到/usr/local/nginx/html/yum下

    
    
    ln -s /mnt/yum/ /usr/local/nginx/html/yum
    

![image.png](https://image.3001.net/images/20210430/1619774709_608bccf5214adfca8714f.png!small)

让浏览器可以遍历yum目录，修改/usr/local/nginx/conf/nginx.conf,在location部分添加

    
    
    autoindex on;
    

![image.png](https://image.3001.net/images/20210430/1619774719_608bccffb7ea341cdec54.png!small)

重启nginx

    
    
    cd /usr/local/nginx/sbin/
    ./nginx -t	#加载配置文件
    ./nginx	#启动nginx
    访问	http://192.168.43.139/yum/
    

![image.png](https://image.3001.net/images/20210430/1619774736_608bcd102738a7d9fe999.png!small)

开启另一台linux服务器，配置yum源，备份本地repo文件

    
    
    mkdir /opt/centos-yum.bak
    mv /etc/yum.repos.d/* /opt/centos-yum.bak/
    

![image.png](https://image.3001.net/images/20210430/1619774748_608bcd1c4a382d511a47a.png!small)

在/etc/yum.repos.d/创建repo文件，添加如下内容

    
    
    vi /etc/yum.repos.d/my.repo
    [base]
    name=CentOS-$releasever - Base
    baseurl=http://192.168.43.139/yum/
    gpgcheck=1
    gpgkey=http://192.168.43.139/yum/RPM-GPG-KEY-CentOS-7
    

![image.png](https://image.3001.net/images/20210430/1619774761_608bcd29f3d1a66570a70.png!small)

清除缓存，把yum源缓存到本地

    
    
    yum clean all	清除缓存
    yum makecache 	把yum源缓存到本地
    yum repolist	查看yum源信息
    yum list		列出可以通过yum源安装的包
    

![image.png](https://image.3001.net/images/20210430/1619774774_608bcd3655ee3da705894.png!small)

使用yum源安装telnet

    
    
    yum install -y telnet
    

![image.png](https://image.3001.net/images/20210430/1619774785_608bcd41929b1cd282f67.png!small)

成功可以使用yum源  
使用其他主机的yum源时，需注意要保证可以和客户端通信！！！

