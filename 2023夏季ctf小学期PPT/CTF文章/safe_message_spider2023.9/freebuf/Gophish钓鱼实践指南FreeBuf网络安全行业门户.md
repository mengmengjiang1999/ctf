## 1\. **概念**

### 1.1. **钓鱼邮件**

指利用伪装的电邮，欺骗收件人将账号、口令等信息回复给指定的接收者；或引导收件人连接到特制的网页，这些网页通常会伪装成和真实网站一样，如银行或理财的网页，令登录者信以为真，输入信用卡或银行卡号码、账户名称及密码等而被盗取。

### 1.2. **社会工程学攻击**

指的是通过与他人的合法地交流，来使其心理受到影响，做出某些动作或者是透露一些机密信息的方式。这通常被认为是一种欺诈他人以收集信息、行骗和入侵计算机系统的行为。

### 1.3. **Gophish**

Gophish is an open-source phishing toolkit designed for businesses and
penetration testers. It provides the ability to quickly and easily setup and
execute phishing engagements and security awareness
training.(Gophish是一个开源网络钓鱼工具包，专为企业和渗透测试人员设计。它提供了快速、轻松地设置和执行网络钓鱼活动和安全意识培训的能力。)

项目地址：<https://github.com/gophish/gophish>

用户手册：[https://docs.getgophish.com/user-guide/﻿](https://docs.getgophish.com/user-guide/)

### 1.4. **Postfix**

是Wietse Venema在IBM的GPL协议之下开发的MTA（邮件传输代理）软件。

### 1.5. **Dovecot**

是一个开源的 IMAP 和 POP3 邮件服务器，支持 Linux/Unix 系统。

## 2\. **环境**

名称

|

操作系统

|

IP

|

Hostname  
  
---|---|---|---  
  
攻击者

|

CentOS Linux release 7.2.1511 (Core)

|

192.168.6.128

|

mail.dia0yu.com  
  
企业A邮件服务器

|

CentOS Linux release 7.2.1511 (Core)

|

192.168.6.129

|

mail.diaoyu.com  
  
## 3\. **场景设定**

假设企业A的域名为diaoyu.com，该企业有张三、李四这两名员工，邮箱账号为zhangsan@diaoyu.com、lisi@diaoyu.com。

现模拟： 攻击者伪造一个假的邮箱security@dia0yu.com,通过该邮箱给张三、李四发送钓鱼邮件。

## 4\. **企业A邮件服务器配置**

### 4.1. **ip**

192.168.6.129

### 4.2. **设置主机名**

hostnamectl set-hostname mail.diaoyu.com

### 4.3. **关闭防火墙**

systemctl stop firewalld

### 4.4. **DNS**

4.4.1. **安装**

    
    
    yum install bind -y

![](https://image.3001.net/images/20210604/1622822385_60ba4df1cdb57cccba7ad.jpg!small)

4.4.2. **修改配置文件**

#### 4.4.2.1. **/etc/named.conf**

    
    
    vi /etc/named.conf

![](https://image.3001.net/images/20210605/1622822436_60ba4e24865ead726ebc5.jpg!small)

检查语法错误

    
    
    named-checkconf

#### 4.4.2.2. **/etc/named.rfc1912.zones**

    
    
    vi /etc/named.rfc1912.zones

在文末添加

![](https://image.3001.net/images/20210605/1622822478_60ba4e4e22c4076205af1.jpg!small)

  

检查语法错误

    
    
    named-checkconf

4.4.2.3. **diaoyu** **.com.zone**

创建正向区域数据配置文件

    
    
    cd /var/named
    
    cp -p named.localhost diaoyu.com.zone

编辑正向区域数据配置文件

    
    
    vi diaoyu.com.zone
    
    
    $TTL 1D
    @	IN SOA	@ rname.invalid. (
    					0	; serial
    					1D	; refresh
    					1H	; retry
    					1W	; expire
    					3H )	; minimum
    	NS	mail.diaoyu.com.
    	MX 10 	mail.diaoyu.com.
    mail	IN A 	192.168.6.129

4.4.2.4. **diaoyu.com.local**

创建反向区域数据配置文件

    
    
    cd /var/named
    
    cp -p named.localhost diaoyu.com.local

编辑反向区域数据配置文件

    
    
    vi diaoyu.com.local
    
    
    $TTL 1D
    @	IN SOA	diaoyu.com rname.invalid. (
    					0	; serial
    					1D	; refresh
    					1H	; retry
    					1W	; expire
    					3H )	; minimum
    	NS	mail.diaoyu.com.
    	MX 10   mail.diaoyu.com.
    10 	PTR 	mail.diaoyu.com.

检查语法错误

    
    
    named-checkconf

4.4.3. **启动** **dns**

    
    
    systemctl start named

4.4.4. **设置开机自启**

    
    
    systemctl enable named

4.4.5. **设置** **dns**

    
    
    vi /etc/resolv.conf

![](https://image.3001.net/images/20210605/1622822520_60ba4e783a2b621edbc77.jpg!small)

4.4.6. **解析验证**

nslookup mail.diaoyu.com

![](https://image.3001.net/images/20210605/1622822567_60ba4ea77c774e1ec6339.jpg!small)

### 4.5. **Postfix**

4.5.1. **修改配置文件**

4.5.1.1. **/etc/postfix/main.cf**

编辑postfix配置文件（修改6处内容）

    
    
    myhostname = mail.diaoyu.com
    
    mydomain = diaoyu.com
    
    myorigin = $mydomain
    
    inet_interfaces =  192.168.6.129 , 127.0.0.1
    
    mydestination = $myhostname,  $mydomain
    
    home_mailbox = Maildir/

检查语法错误

postfix check

4.5.2. **重启服务**

systemctl restart postfix

4.5.3. **加入开机自启**

systemctl enable postfix

4.5.4. **查看postfix配置**

postconf -n

![](https://image.3001.net/images/20210605/1622822602_60ba4eca1d88b8aee73cb.jpg!small)

4.5.5. **新建用户**

新建系统用户(系统账号即为邮件账号) test、diaoyu、zhangsan、lisi

![](https://image.3001.net/images/20210605/1622822637_60ba4eed3e5143bf2d7a3.jpg!small)

### 4.6. **Dovecot**

4.6.1. **安装**

    
    
    yum install -y dovecot

![](https://image.3001.net/images/20210605/1622822686_60ba4f1eb83af8068eb9f.jpg!small)

4.6.2. **修改配置文件**

#### 4.6.2.1. **/etc/dovecot/dovecot.conf**

    
    
    protocols = imap pop3 lmtp
    
    listen = *
    
    !include conf.d/10-auth.conf
    
    ssl = no
    
    disable_plaintext_auth = no
    
    mail_location = maildir:~/Maildir

4.6.3. **启动服务**

systemctl start dovecot

4.6.4. **加入开机自启**

systemctl enable dovecot

### 4.7. **检查端口监听情况**

110，143端口需要监听

![](https://image.3001.net/images/20210605/1622822715_60ba4f3be82a5049ad3e0.jpg!small)

### 4.8. **测试发邮件**

telnet 发件测试

![](https://image.3001.net/images/20210605/1622822787_60ba4f83006aecf4f8f5f.jpg!small)

使用Foxmail（宿主机）添加邮箱，结果失败：

![](https://image.3001.net/images/20210605/1622822842_60ba4fba4f7e87eb06c33.jpg!small)

宿主机无法Telnet 25端口

![](https://image.3001.net/images/20210605/1622822878_60ba4fde98d15385f79a3.jpg!small)

检查发现防火墙开启，关闭防火墙

![](https://image.3001.net/images/20210605/1622822915_60ba5003b977673e707bf.jpg!small)

宿主机再次Telnet 发现已成功

![](https://image.3001.net/images/20210605/1622822955_60ba502b1e89cd7d84b31.jpg!small)

Foxmail成功创建账号

![](https://image.3001.net/images/20210605/1622823007_60ba505fba98fe034395b.jpg!small)

收到的邮件信息如下

![](https://image.3001.net/images/20210605/1622823129_60ba50d97e049c0100a3e.jpg!small)

现使用diaoyu@dia0yu.com,发送邮件给diaoyu@diao.com,提示Undelivered Mail Returned to
Sender（系统退信）[在攻击机named.rfc1912.zones增加内容后问题解决]。

![](https://image.3001.net/images/20210605/1622823170_60ba51024751ad7bdba89.jpg!small)

打开eml可以看到以下内容

![](https://image.3001.net/images/20210605/1622823199_60ba511f595d0869d25bf.jpg!small)

## 5\. **攻击机配置**

### 5.1. **ip**

192.168.6.128

### 5.2. **Hostname**

mail.dia0yu.com

### 5.3. **DNS**

5.3.1. **修改配置文件**

#### 5.3.1.1. **/etc/named.rfc1912.zones**

最终文件内容为：

    
    
    // named.rfc1912.zones:
    //
    // Provided by Red Hat caching-nameserver package 
    //
    // ISC BIND named zone configuration for zones recommended by
    // RFC 1912 section 4.1 : localhost TLDs and address zones
    // and http://www.ietf.org/internet-drafts/draft-ietf-dnsop-default-local-zones-02.txt
    // (c)2007 R W Franks
    // 
    // See /usr/share/doc/bind*/sample/ for example named configuration files.
    //
    
    zone "localhost.localdomain" IN {
    	type master;
    	file "named.localhost";
    	allow-update { none; };
    };
    
    zone "localhost" IN {
    	type master;
    	file "named.localhost";
    	allow-update { none; };
    };
    
    zone "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa" IN {
    	type master;
    	file "named.loopback";
    	allow-update { none; };
    };
    
    zone "1.0.0.127.in-addr.arpa" IN {
    	type master;
    	file "named.loopback";
    	allow-update { none; };
    };
    
    zone "0.in-addr.arpa" IN {
    	type master;
    	file "named.empty";
    	allow-update { none; };
    };
    zone "dia0yu.com" IN {
    	type master;
    	file "dia0yu.com.zone";
    };
    zone "6.168.192.in-addr.arpa" {
    	type master;
    	file "dia0yu.com.local";
    };
    zone "diaoyu.com" IN {
    	type master;
    	file "diaoyu.com.zone";
    };

5.3.2. **/etc/resolv.conf**

cat /etc/resolv.conf

![](https://image.3001.net/images/20210605/1622823319_60ba5197870d21cec478e.jpg!small)

5.3.3. **diaoyu.com.zone**

cd /var/named/

cat diaoyu.com.zone

    
    
    $TTL 1D
    @	IN SOA	@  rname.invalid. (
    					0	; serial
    					1D	; refresh
    					1H	; retry
    					1W	; expire
    					3H )	; minimum
    	NS	@
    	A	192.168.6.129
    	MX 10 	mail
    mail	A	192.168.6.129

5.3.4. **dia** **0** **yu.com.local**

cd /var/named

    
    
    [root@127 named]# cat dia0yu.com.local 
    $TTL 1D
    @	IN SOA	diaoyu.com rname.invalid. (
    					0	; serial
    					1D	; refresh
    					1H	; retry
    					1W	; expire
    					3H )	; minimum
    	NS	mail.dia0yu.com.
    	MX 10   mail.dia0yu.com.
    10 	PTR 	mail.dia0yu.com.

5.3.5. **dia** **0** **yu.com.zone**

cd /var/named

    
    
    [root@127 named]# cat dia0yu.com.zone 
    $TTL 1D
    @	IN SOA	@ rname.invalid. (
    					0	; serial
    					1D	; refresh
    					1H	; retry
    					1W	; expire
    					3H )	; minimum
    	NS	mail.dia0yu.com.
    	MX 10 	mail.dia0yu.com.
    mail	IN A 	192.168.6.128

### 5.4. **互发邮件测试**

成功使用邮箱dia0yu@dia0yu.com发送邮件给diaoyu@diaoyu.com

![](https://image.3001.net/images/20210605/1622823346_60ba51b20e630765d106b.jpg!small)

### 5.5. **其他**

postfix、dovecot配置与企业A邮件服务器配置类似

如Telnet端口不通，请检查防火墙状态

## 6\. **Gophish**

### 6.1. **下载**

wget
[_https://github.com/gophish/gophish/releases/download/v0.11.0/gophish-v0.11.0-linux-64bit.zip_](https://github.com/gophish/gophish/releases/download/v0.11.0/gophish-v0.11.0-linux-64bit.zip)

![](https://image.3001.net/images/20210605/1622823386_60ba51dac3655e8d23c71.jpg!small)

### 6.2. **解压**

unzip gophish-v0.11.0-linux-64bit.zip

![](https://image.3001.net/images/20210605/1622823413_60ba51f5c4bc35df3fcc6.jpg!small)

### 6.3. **config.json**

修改配置文件

    
    
    [root@mail gophish]# cat config.json 
    {
    	"admin_server": {
    		"listen_url": "0.0.0.0:3333",
    		"use_tls": true,
    		"cert_path": "gophish_admin.crt",
    		"key_path": "gophish_admin.key"
    	},
    	"phish_server": {
    		"listen_url": "0.0.0.0:80",
    		"use_tls": false,
    		"cert_path": "example.crt",
    		"key_path": "example.key"
    	},
    	"db_name": "sqlite3",
    	"db_path": "gophish.db",
    	"migrations_prefix": "db/db_",
    	"contact_address": "",
    	"logging": {
    		"filename": "",
    		"level": ""
    	}
    }

### 6.4. **修改文件权限**

chmod +x gophish

### 6.5. **访问**

访问后台：https://ip:3333

![](https://image.3001.net/images/20210605/1622823462_60ba5226d53b7dac8067c.jpg!small)

新版gophish，登录密码在终端中体现：

![](https://image.3001.net/images/20210605/1622823492_60ba5244c2b341c59def3.jpg!small)

首次登录需修改密码

![](https://image.3001.net/images/20210605/1622823521_60ba526110b537cf67251.jpg!small)

成功登录后台

![](https://image.3001.net/images/20210605/1622823547_60ba527ba077a965d2ce8.jpg!small)

### 6.6. **Users & Groups**

添加用户组

![](https://image.3001.net/images/20210605/1622823618_60ba52c21851b3b74ecc8.jpg!small)

### 6.7. **Sending Profiles**

配置发件人信息，以实际情况填写

![](https://image.3001.net/images/20210605/1622823646_60ba52deb0a9e0175d822.jpg!small)

可以发送测试邮件看是否可以正常发送邮件

![](https://image.3001.net/images/20210605/1622823682_60ba530258b3025939494.jpg!small)

可以看到张三收到了gophish发来的测试邮件

![](https://image.3001.net/images/20210605/1622823720_60ba5328d31c5e37ada2c.jpg!small)

### 6.8. **Landing Pages**

设置钓鱼页面，此处支持一键导入，和人工手写HTML

Capture Submitted Data 捕获数据

Capture Passwords 捕获密码

Redirect to: 当受害者点击提交后跳转到的URL

![](https://image.3001.net/images/20210605/1622823755_60ba534ba0150a6696d75.jpg!small)![](https://image.3001.net/images/20210605/1622823786_60ba536a373524393a528.jpg!small)

查看钓鱼页面：

![](https://image.3001.net/images/20210605/1622823815_60ba53872c6f9a864c640.jpg!small)

### 6.9. **Email Templates**

配置邮件正文，此处可以使用其他邮箱写好邮件，导出eml格式后导入

![](https://image.3001.net/images/20210605/1622823858_60ba53b295fc446e803df.jpg!small)

![](https://image.3001.net/images/20210605/1622823905_60ba53e16590e085dd58e.jpg!small)

复制eml文件后粘贴到此处

![](https://image.3001.net/images/20210605/1622823935_60ba53ff27fe654221f5d.jpg!small)

此处导入出现乱码，改成直接填写内容：

![](https://image.3001.net/images/20210605/1622823962_60ba541ac93ccef3b40d7.jpg!small)

此处的完整HTML为：

    
    
    <html>
    <head>
    	<title></title>
    </head>
    <body>
    <p>您好：</p>
    
    <p>近期检测到您在学者网教学科研协作单位平台的密码已过期， 请点击<a href="{{.URL}}">此链接</a>尽快修改密码，谢谢配合！</p>
    {{.Tracker}}</body>
    </html>

还可以增加附件：

![](https://image.3001.net/images/20210605/1622823999_60ba543fbbf529c805971.jpg!small)

### 6.10. **Campaigns**

创建任务发送钓鱼邮件，可设置分批发送邮件（Launch Date）

![](https://image.3001.net/images/20210605/1622824044_60ba546c6d2cd4326f3e7.jpg!small)

![](https://image.3001.net/images/20210605/1622824074_60ba548a9ddfca3c20278.jpg!small)

管理页面，可以看到成功发出2封邮件。

![](https://image.3001.net/images/20210605/1622824097_60ba54a15966e0522d874.jpg!small)

张三成功收到钓鱼邮件

![](https://image.3001.net/images/20210605/1622824127_60ba54bf530ddd0c8a298.jpg!small)

如果张三安全意识不足，点击链接打开，则会看到以下页面

![](https://image.3001.net/images/20210605/1622824178_60ba54f2325108872b072.jpg!small)

然后张三就真的输入了账号及密码，点击了login

![](https://image.3001.net/images/20210605/1622824205_60ba550dd66b1b2bd2d5d.jpg!small)

点完张三发现，怎么又让我登录！

没错，此时钓鱼已经完成，当张三点击login后，钓鱼页面自动跳转到真正的系统：

![](https://image.3001.net/images/20210605/1622824244_60ba5534d856fb0ae10ab.jpg!small)

再次刷新Gophish后台，！ ! ! 张三中招了！

![](https://image.3001.net/images/20210605/1622824293_60ba55654a6cc19670abe.jpg!small)

我们可以查看张三提交的数据

![](https://image.3001.net/images/20210605/1622824325_60ba5585d864d1eb3721b.jpg!small)

![](https://image.3001.net/images/20210605/1622824357_60ba55a54aa8e402e7a42.jpg!small)

至此，钓鱼完成！ 我们成功搞到了张三的密码！

![](https://image.3001.net/images/20210605/1622824381_60ba55bdeb4e86e2cacf6.jpg!small)

## 7\. **利用场景**

### 7.1. **攻防演习**

正面攻击越来越难时，社会工程学攻击变得越来越流行。据某安全人员消息，今年的攻防演习中，他们队有接近70%的分数是靠社会工程学攻击获取到。而钓鱼邮件，则是最常用的手段之一。

### 7.2. **企业安全意识教育培训**

企业安全团队计划开展公司全员安全意识教育培训，不妨先开展一次这样的钓鱼邮件测试，我想这是最好的培训素材，也能够让员工体会更深，对安全意识的理解更加深刻。

### 7.3. **红蓝对抗**

当面对防守方互联网侧资产束手无策时，一封钓鱼邮件发过去，说不定可以带来惊喜呢？！一旦有人运行了钓鱼邮件中的附件，CS上线它不香吗？

### 7.4. **客户需求**

客户需要对公司的人员进行钓鱼邮件测试，来检测员工的网络安全意识，避免在真正的攻击中因为钓鱼而使系统被攻陷。

## 8\. **钓鱼模板**

### 8.1. **重置密码**

攻击者伪装成管理员，让受害者点击钓鱼邮件中的链接来修改各种各样的密码！如下：

![](https://image.3001.net/images/20210605/1622824452_60ba560467c7bae450c99.jpg!small)

![](https://image.3001.net/images/20210605/1622824484_60ba562447a0357522828.jpg!small)

![](https://image.3001.net/images/20210605/1622824510_60ba563ea543669853afd.jpg!small)

### 8.2. **账号解冻**

攻击者伪装成系统管理员，让受害者点击钓鱼邮件中的链接解冻账号。

![](https://image.3001.net/images/20210605/1622824533_60ba565531160a4665891.jpg!small)

### 8.3. **升级补丁**

攻击者伪装成系统管理员，让受害者点击钓鱼邮件中的附件 升级补丁。

![](https://image.3001.net/images/20210605/1622824560_60ba5670ca3adbbdccfb2.jpg!small)

### 8.4. **信息收集**

利用疫情，让受害者点击钓鱼邮件中的链接反馈相关信息。

![](https://image.3001.net/images/20210605/1622824604_60ba569cdc21f9ff889a0.jpg!small)

### 8.5. **节假日礼包**

攻击者伪装成公司员工，让受害者点击钓鱼邮件中的链接领取节假日大礼包。

### 8.6. **系统扩容**

攻击者伪装成系统管理员，让受害者点击钓鱼邮件中的链接升级扩容（如扩容邮箱容量）。

### 8.7. **升级改造**

![](https://image.3001.net/images/20210605/1622824657_60ba56d15dae784c7daf8.jpg!small)

### 8.8. **登录异常**

![](https://image.3001.net/images/20210605/1622824682_60ba56ea31132716f3e05.jpg!small)

### 8.9. **其他**

![](https://image.3001.net/images/20210605/1622824708_60ba570470324933f37e8.jpg!small)

## 9\. **防范**

那遇到这样的钓鱼邮件应该如何防范?

以本文的钓鱼邮件为例，我们可以从以下几点去识别钓鱼邮件。

> 识别发件人的邮箱后缀是否是本公司邮箱后缀（如未开启SPF则公司邮箱后缀可以伪造）
>
> 右键查看链接地址是否为假冒的地址
>
> 工作中如果收到可疑邮件，应及时联系安全部门或相关责任部门，不要随意点击邮件中的链接、下载邮件中的附件、运行附件等危险操作！

![](https://image.3001.net/images/20210605/1622824747_60ba572ba0bcf46e9d7b0.jpg!small)

## 10\. **免责声明**

本文仅限技术分享，严禁用于非法用途，否则产生的一切后果自行承担。

## 11\. **参考致谢**

部分素材源自网络，侵删。

[
_https://blog.51cto.com/u_12227558/2074095_](https://blog.51cto.com/u_12227558/2074095)

[ _https://xz.aliyun.com/t/5412_](https://xz.aliyun.com/t/5412)

[
_http://www.360doc.cn/mip/947685395.html_](http://www.360doc.cn/mip/947685395.html)

