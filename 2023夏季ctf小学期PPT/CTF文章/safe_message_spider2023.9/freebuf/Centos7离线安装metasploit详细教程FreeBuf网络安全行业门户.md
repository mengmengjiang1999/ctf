**最近需在内网服务器搭建安全工具环境，苦于内网服务器无法访问互联网，需要很多依赖包比较麻烦，尤其metasploit无互联网安装特别麻烦，而且网上metasploit的安装教程均是在线一键安装教程，对于无法访问互联网的服务器进行安装均无效，经过多次测试终于完成离线安装，先整理了下安装过程步骤。**

建议在能访问互联网的环境里先按照步骤安装一遍，即能熟悉安装过程又能下载所需的软件包和各种依赖包。

## 一、准备工作

以下均在能连通互联网的linux主机上操作：

> 1）下载最新yaml：wget <http://pyyaml.org/download/libyaml/yaml-0.2.2.tar.gz>
>
> 2）下载最新ruby：wget <http://ftp.ruby-> lang.org/pub/ruby/2.7/ruby-2.7.0-preview1.tar.gz>
>
> 3）下载依赖包，使用yum下载不安装命令，下载相关依赖于目录/opt/devel中：

yum install sqlite-devel libxslt-devel libxml2-devel java-1.7.0-openjdk
libpcap-devel nano openssl-devel zlib-devel libffi-devel gdbm-devel readline-devel nano --downloadonly --downloaddir=/opt/devel

![1567653615_5d707eef59e5e.png!small](https://image.3001.net/images/20190905/1567653615_5d707eef59e5e.png!small)

![1567653621_5d707ef507d4e.png!small](https://image.3001.net/images/20190905/1567653621_5d707ef507d4e.png!small)
4）下载PostgreSQL RPM Building Project - Repository Packages（centos7）：

<https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm>

安装：rpm -ivh pgdg-redhat-repo-latest.noarch.rpm

5）下载postgresql-11，使用yum下载不安装命令，下载postgresql-11及相关依赖于目录/opt/postgresql中：

yum install postgresql11-server --downloadonly --downloaddir=/opt/postgresql

6）下载metasploit

在github下载：

<https://github.com/rapid7/metasploit-framework/archive/master.zip>

## 二、安装步骤

### 1、安装依赖

1）安装'Development Tools'

yum groupinstall 'Development Tools'

2）安装上面下载在/opt/devel目录的依赖包：

    
    
    cd  /opt/devel
    
    yum   install  -y   ./*            //安装所有依赖包

此处注意，如果测试互联网主机为centos系统，内网主机为redhat系统，注意先删除下载的centos-release-7-6.1810.2.el7.centos.x86_64.rpm此文件，再yum安装。

### 2、yaml安装教程

将下载的yaml-0.2.2.tar.gz 复制到内网主机的目录/usr/src

    
    
    cd /usr/src
    
    tar zxvf yaml-0.2.2.tar.gz       
    
    cd yaml-0.2.2
    
    ./configure --prefix=/usr/local
    
    make && make install

### 3、ruby安装教程

将下载的ruby-2.7.0-preview1.tar.gz 复制到内网主机的目录/usr/src

    
    
    cd /usr/src
    
    tar zxvf ruby-2.7.0-preview1.tar.gz 
    
    ./configure --prefix=/usr/local  --with-opt-dir=/usr/local/lib
    
    make && make install

### 4、安装postgresql-11

将下载的postgresql-11软件及依赖包拷贝至内网主机的目录/opt/postgresql

    
    
    cd  /opt/postgresql
    
    yum install -y ./*                //安装所有postgresql-11软件及依赖包

此处注意，如果测试互联网主机为centos系统，内网主机为redhat系统，注意先删除下载的centos-release-7-6.1810.2.el7.centos.x86_64.rpm此文件，再yum安装。

![1567653635_5d707f03b2608.png!small](https://image.3001.net/images/20190905/1567653635_5d707f03b2608.png!small)

/usr/pgsql-11/bin/postgresql-11-setup initdb //初始化数据库

![1567653640_5d707f08e7053.png!small](https://image.3001.net/images/20190905/1567653640_5d707f08e7053.png!small)

systemctl enable postgresql-11.service //服务开机启动

systemctl start postgresql-11.service //启动服务

systemctl status postgresql-11.service //查看服务状态

![1567653645_5d707f0d4d529.png!small](https://image.3001.net/images/20190905/1567653645_5d707f0d4d529.png!small)因为编译ruby所必须的gem时，需要把新安装的加入路径，这样编译器就能找到库和二进制文件，执行命令：

    
    
    echo export PATH=/usr/pgsql-11/bin:\$PATH  >> /etc/bashrc 
    
    source ~/.bashrc

切换到Postgres用户，创建我们将要用于Metasploit的用户名和数据库，命令如下：

    
    
    su  -  postgres
    
    createuser msf -P -S -R -D      //创建用户msf，会提示输入密码
    
    createdb -O msf msf             //创建数据库
    
    exit

为允许我们创建的用户能够连接Postgresql，我们需要设置一下pg_hba.conf文件，命令如下：

    
    
    vim /var/lib/pgsql/11/data/pg_hba.conf

需要的添加的内容如下：

    
    
    local  msf   msf    md5
    
    host   msf   msf 127.0.0.1/32   md5
    
    host   msf   msf ::1/128   md5
    
     
    
    systemctl  restart  postgresql-11.service     //重启postgresql服务

### 5、下载Metasploit依赖的Ruby库（在互联网主机上操作）

gem install wirble pg sqlite3 msgpack activerecord redcarpet rspec simplecov
yard bundler

将自动加载在本地的gem包拷贝出来供内网使用，目录：/usr/local/lib/ruby/gems/2.7.0/cache

将此目录中的所有文件拷贝出供内网主机安装使用。

 **在内网主机：**

    
    
     cd   /opt/cache        //拷贝gem包的目录
    
    gem install -l  wirble pg sqlite3 msgpack activerecord redcarpet rspec simplecov yard bundler   // -l 本地安装

 **在** **安装** **过程中遇到如下报错** **（** **附解决办法** **）** **：**

1）zlib报错

![1567653653_5d707f1558fc9.png!small](https://image.3001.net/images/20190905/1567653653_5d707f1558fc9.png!small)

解决办法：

    
    
    yum  install  zlib-devel     //安装依赖包zlib-devel
    
    cd  /usr/src/ruby-2.7.0-preview1/ext/zlib    //进入ruby的软件包解压目录的ext/zlib目录中
    
    ruby  extconf.rb 
    
    make&&make  install

2）openssl报错

![1567653657_5d707f19e1f57.png!small](https://image.3001.net/images/20190905/1567653657_5d707f19e1f57.png!small)

解决办法：

    
    
    yum  install   openssl-devel    //安装依赖包 openssl-devel
    
    cd   /usr/src/ruby-2.7.0-preview1/ruby-2.3.8/ext/openssl  //进入ruby的软件包解压目录的ext/openssl目录中
    
    ruby   extconf.rb 
    
    make&&make  install

3）pg报错（缺少依赖）

    
    
    cd  /opt/postgresql                 //进入postgresql下载的目录
    
    yum  install  postgresql-devel       //安装依赖postgresql-devel

### 6、Metasploit安装

    
    
    cd  /opt              //metasploit-framework-master.zip放置的目录
    
    unzip  metasploit-framework-master.zip
    
    mv  metasploit-framework-master    metasploit-framework    //修改解压后的目录名
    
    cd  /opt/metasploit-framework

1）为了在终端下也能运行，创建软链接；命令如下：

    
    
    bash -c 'for MSF in $(ls msf*); do ln -s /opt/metasploit-framework/$MSF /usr/local/bin/$MSF;done'
    
    ln  -s  /opt/metasploit-framework/armitage /usr/local/bin/armitage

2）在终端下，进入Metasploit的文件中，使用Bundler Gem来安装合适的Gem版本：（在互联网主机上操作）

    
    
    cd  /opt/metasploit-framework
    
    bundle   install       //需较长时间

将自动加载在本地的gem包拷贝出来供内网使用，目录：/usr/local/lib/ruby/gems/2.7.0/cache

将此目录中的所有文件拷贝出供内网主机安装使用。

    
    
    cd   /usr/local/lib/ruby/gems/2.7.0/cache 
    
    gem  install -l  ./*                 //安装所有的gem文件

3） 创建Metasploit框架将要使用的database.yml，命令如下：

    
    
    vim  /opt/metasploit-framework/database.yml

database.yml中的具体内容如下：

    
    
    　　production:
    
    　　adapter: postgresql
    
    　　database: msf
    
    　　username: msf
    
    　　password: mypass                  //上面创建的用户msf的密码
    
    　　host: 127.0.0.1
    
    　　port: 5432
    
    　　pool: 75
    
    　　timeout: 5

再次执行以下命令，这样就能通过Armitage和msfconsole在当前shell中创建和加载环境变量：

    
    
    echo export MSF_DATABASE_CONFIG=/opt/metasploit-framework/database.yml >> /etc/bashrc
    
    source ~/.bashrc

### 7、 最后，让我们运行已经安装的Metasploit，命令如下：

msfconsole

![1567653666_5d707f2239329.png!small](https://image.3001.net/images/20190905/1567653666_5d707f2239329.png!small)

## 参考链接：

>
> [_https://blog.csdn.net/bnxf00000/article/details/44872709_](https://blog.csdn.net/bnxf00000/article/details/44872709)
>
>
> [_https://www.cnblogs.com/jimcsharp/p/8576766.html_](https://www.cnblogs.com/jimcsharp/p/8576766.html)

 ***本文作者：Tommg唐，转载请注明来自FreeBuf.COM**

