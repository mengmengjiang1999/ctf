## 一、介绍

当学习网络安全时，了解和使用安全设备是必不可少的一部分，其中一种常见的安全设备是Web应用防火墙（WAF）。市场上有许多商业化的WAF，但对于学习目的，我推荐使用一款免费开源的WAF，名为ModSecurity。

ModSecurity是一个开源的、跨平台的Web应用防火墙（WAF），被称为WAF界的“瑞士军刀”。它可以通过检查Web服务接收到的数据，以及发送出去的数据来对网站进行安全防护。

目前已经支持Nginx和IIS，配合Nginx的灵活和高效，可以打造成生产级的WAF，是保护和审核Web安全的利器。

ModSecurity官网下载地址：<http://www.modsecurity.cn/>，我下载的是ModSecurity
v3.0.4的稳定版，v2.9.*的与Nginx存在兼容问题。

## 二、功能

    
    
    SQL Injection (SQLi)：阻止SQL注入  
    Cross Site Scripting (XSS)：阻止跨站脚本攻击  
    Local File Inclusion (LFI)：阻止利用本地文件包含漏洞进行攻击  
    Remote File Inclusione(RFI)：阻止利用远程文件包含漏洞进行攻击  
    Remote Code Execution (RCE)：阻止利用远程命令执行漏洞进行攻击  
    PHP Code Injectiod：阻止PHP代码注入  
    HTTP Protocol Violations：阻止违反HTTP协议的恶意访问  
    HTTPoxy：阻止利用远程代理感染漏洞进行攻击  
    Sshllshock：阻止利用Shellshock漏洞进行攻击  
    Session Fixation：阻止利用Session会话ID不变的漏洞进行攻击  
    Scanner Detection：阻止黑客扫描网站  
    Metadata/Error Leakages：阻止源代码/错误信息泄露  
    Project Honey Pot Blacklist：蜜罐项目黑名单  
    GeoIP Country Blocking：根据判断IP地址归属地来进行IP阻断

## 三、安装与配置

### 1\. 安装后续编译所需依赖

    
    
    yum install -y gcc-c++ flex bison yajl yajl-devel curl-devel curl GeoIP-devel doxygen zlib-devel pcre-devel lmdb-devel libxml2-devel ssdeep-devel lua-devel libtool autoconf automake wget epel-release openssl-devel

### 2\. 安装ModSecurity

    
    
    mkdir -p /usr/local/modsecurity     // -p(parents):父文件夹不存在就创建，省得一级一级地创建  
    ​  
    cd /usr/local/modsecurity   
    wget http://www.modsecurity.cn/download/modsecurity/modsecurity-v3.0.3.tar.gz  
    tar -zxvf modsecurity-v3.0.3.tar.gz  
    ​  
    mv modsecurity-v3.0.3 /usr/local/modsecurity/modsecurity // 改名  
    ​  
    cd /usr/local/modsecurity/modsecurity  
    sh build.sh     // 执行build.sh  
    ./configure     // 配置，无其他参数  
    make && make instal // 编译

### 3\. 安装ModSecurity-Nginx

modsecurity-nginx是 nginx 和 libmodsecurity 之间的连接器,需要安装。

    
    
    cd /usr/local/  
    wget https://codeload.github.com/SpiderLabs/ModSecurity-nginx/zip/refs/heads/master  
    ​  
    yum -y install unzip    // 如果已经有了的话就不必再安装unzip了  
    unzip  master             
    ​  
    mv ModSecurity-nginx-master /usr/local/modsecurity/modsecurity-nginx    // 改名  
    ​

### 4\. 安装Nginx

由于个人原因 需要安装SSL模块 ，如果不需要SSL 可以编译时使用下面 指令进行编译。

    
    
    ./configure --prefix=/usr/local/nginx --add-module=/usr/local/modsecurity-nginx 

开始执行相关命令安装Nginx

    
    
    mkdir -p /usr/local/nginx  
    ​  
    cd /usr/local/nginx  
    wget http://nginx.org/download/nginx-1.22.1.tar.gz  
    tar -zxvf nginx-1.22.1.tar.gz  
    ​  
    cd /usr/local/nginx/nginx-1.22.1/       // 转到该目录  
    ./configure --prefix=/usr/app/nginx --with-http_stub_status_module --with-http_ssl_module --with-file-aio --with-http_realip_module --add-module=/usr/local/modsecurity-nginx   
    ​  
    make && make install

## 四、配置

以上安装均全完成，现在进入配置环节，将ModSecurity 下的配置文件 复制到nginx.config 目录，方便后期更改配置。

    
    
    mkdir -p /usr/local/nginx/conf/modsecurity  
    cp /usr/local/modsecurity/modsecurity/modsecurity.conf-recommended /usr/local/nginx/conf/modsecurit/modsecurity.conf    // 重命名  
    cp /usr/local/modsecurity/modsecurity/unicode.mapping  /usr/app/nginx/conf/modsecurity  // 复制文件

### 1\. 配置nginx.conf

    
    
    vim /usr/local/nginx/conf/nginx.conf

在http或server节点中添加以下内容（在http节点添加表示全局配置，在server节点添加表示为指定网站配置）。

![1689927890_64ba40d235608fa4bbc84.png!small?1689927890499](https://image.3001.net/images/20230721/1689927890_64ba40d235608fa4bbc84.png!small?1689927890499)

我这里就添加到server节点，因为我添加到http节点时打不开Nginx服务，所以我索性就添加到server节点，大家如果遇到和我一样的问题，也可以换一个节点添加内容。

打开规则引擎SecRuleEngine On

    
    
    #SecRuleEngine DetectionOnly  
    SecRuleEngine On

确保ModSecurity在记录审计日志时保存请求体IJ 改为 C

    
    
    #SecAuditLogParts ABIJDEFHZ  
    SecAuditLogParts ABCDEFHZ

添加防护规则文件

    
    
    Include /usr/local/nginx/conf/modsecurity/crs-setup.conf  
    Include /usr/local/nginx/conf/modsecurity/rules/*.conf

![1689927923_64ba40f33185e4231e879.png!small?1689927923151](https://image.3001.net/images/20230721/1689927923_64ba40f33185e4231e879.png!small?1689927923151)

### 2.下载防护规则文件

    
    
    cd /usr/app/modsecurity  
    wget http://www.modsecurity.cn/download/corerule/owasp-modsecurity-crs-3.3-dev.zip  // 无论是ModSecurity是1.6.1版本还是1.22.1版本都可以用这个规则文件，亲测可用。  
    unzip owasp-modsecurity-crs-3.3-dev.zip  
    ​  
    cd owasp-modsecurity-crs-3.3-dev
    
    
    cp crs-setup.conf.example /usr/local/nginx/conf/modsecurity/crs-setup.conf  // 复制并改名
    
    
    cp -r rules /usr/app/nginx/conf/modsecurity/  
    cd /usr/local/nginx/conf/modsecurity/rules  
    ​  
    mv REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf.example REQUEST-900-EXCLUSION-RULES-BEFORE-CRS.conf  
    mv RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf.example RESPONSE-999-EXCLUSION-RULES-AFTER-CRS.conf

## 四、测试

### 1\. 启动Nginx

    
    
    /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf  
    ​  
    注：如果启动不了，试试用systemctl service start Nginx 来启动服务

Nginx 常用命令如下：

    
    
    # 启动 Nginx  
    systemctl start nginx  
    ​  
    # 停止 Nginx  
    systemctl stop nginx  
    ​  
    # 重启 Nginx  
    systemctl restart nginx  
    ​  
    # 查看 Nginx 状态  
    systemctl status nginx

### 2\. 测试防护效果

    
    
    curl -I http://localhost 

返回状态码200，代表正常访问成功，Nginx首页内容：

    
    
    HTTP/1.1 200 OK  
    Server: nginx/1.22.1  
    Date: Wed, 19 Jul 2023 12:43:40 GMT  
    Content-Type: text/html  
    Content-Length: 615  
    Last-Modified: Wed, 19 Jul 2023 11:18:47 GMT  
    Connection: keep-alive  
    ETag: "64b7c697-267"  
    Accept-Ranges: bytes

试一下SQL注入攻击

返回状态码是400，被拦截了，说明WAF起作用了

    
    
    HTTP/1.1 400 Bad Request
    Server: nginx/1.22.1
    Date: Wed, 19 Jul 2023 12:45:33 GMT
    Content-Type: text/html
    Content-Length: 157
    Connection: close

至此，在CentOS7中安装ModSecurity+Nginx就结束了，如果有什么不足之处还望指正，谢谢。

 **参考链接：**

[CentOS 7.X 网络安全加固 Nginx 安装 ModSecurity 模块 - 龙凌云端 - 博客园
(cnblogs.com)](https://www.cnblogs.com/miracle-luna/p/17204007.html)

  

  

