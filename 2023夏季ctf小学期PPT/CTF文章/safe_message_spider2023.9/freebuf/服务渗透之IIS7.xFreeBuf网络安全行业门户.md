> 环境：windows7、IIS7.x
>
> 获取工具方式(微信rx6662)：

1.解析漏洞使用工具：FastCGI设置

2.HTTP.SYS远程代码执行工具：MSF15-034、MSF读取内存数据

3.认证绕过漏洞：匿名访问设置

行为图（活动图）：

![1620183946_60920b8a77421b469f264.png!small](https://image.3001.net/images/20210505/1620183946_60920b8a77421b469f264.png!small)

环境搭建：

1.开启IIS7.5的功能

![1620184699_60920e7bb16c64489f6e7.png!small](https://image.3001.net/images/20210505/1620184699_60920e7bb16c64489f6e7.png!small)

2.IIS7.5启动成功（访问地址：http://服务器地址:80/）![1620184840_60920f08b9d3717213fe2.png!small](https://image.3001.net/images/20210505/1620184840_60920f08b9d3717213fe2.png!small)

3.IIS和PHP联动有两种方法：phpstudy，IIS添加php-cgi

## 一、IIS联动php

（1）在IIS7.5添加php-cgi---IIS

![1620185061_60920fe58bfbd1628cf4b.png!small](https://image.3001.net/images/20210505/1620185061_60920fe58bfbd1628cf4b.png!small)

![1620185118_6092101ea6f51b79e5e55.png!small](https://image.3001.net/images/20210505/1620185118_6092101ea6f51b79e5e55.png!small)

（2）在IIS主目录写inetpub-》wwwroot目录下创建phpinfo.php文件，并访问成功---IIS

![1620185321_609210e98d55c852685fc.png!small](https://image.3001.net/images/20210505/1620185321_609210e98d55c852685fc.png!small)

## 二、phpstudy环境配置联动IIS

（1）下载安装小皮phpstudy2016版（http://public.xp.cn/upgrades/phpStudy20161103.zip），并安装

![1620185658_6092123af39eac47d684f.png!small](https://image.3001.net/images/20210505/1620185658_6092123af39eac47d684f.png!small)

（2）如果遇到安装不成缺少vc9,需要下载插件（https://xcdn.php.cn/gongju/fuwuqi/32%E4%BD%8Dvc9%E5%92%8C11%E3%80%8114%E8%BF%90%E8%A1%8C%E5%BA%93.zip?sign=aa3bcd53cce3e07faa35199648e62a83&amptimestamp=1620120191）直接安装32位vc9即可

（3）切换到php 5.2.17-php7/8联动版本

![1620185841_609212f1ad40d453385fe.png!small](https://image.3001.net/images/20210505/1620185841_609212f1ad40d453385fe.png!small)

（4）phpstudy联动版默认开启的8980端口

![1620186401_6092152137b3f690df29d.png!small](https://image.3001.net/images/20210505/1620186401_6092152137b3f690df29d.png!small)

漏洞：

### 1.文件解析漏洞

IIS7.x版本，在Fast-CGI运行模式下，存在任意文件解析漏洞，只用在访问文件的后面“/.php”就会被当成php文件解析。

（1）在IIS-wwwroot根目录下创建png文件，并访问

![1620186864_609216f038bce31c7502a.png!small](https://image.3001.net/images/20210505/1620186864_609216f038bce31c7502a.png!small)

![1620187071_609217bfbca0fdee37b9b.png!small](https://image.3001.net/images/20210505/1620187071_609217bfbca0fdee37b9b.png!small)

![1620187236_60921864473d24f5e72b8.png!small](https://image.3001.net/images/20210505/1620187236_60921864473d24f5e72b8.png!small)

![1620187304_609218a82e9ecbd9b1b4e.png!small](https://image.3001.net/images/20210505/1620187304_609218a82e9ecbd9b1b4e.png!small)

![1620187384_609218f84a1b071ada8cc.png!small](https://image.3001.net/images/20210505/1620187384_609218f84a1b071ada8cc.png!small)

修复建议

（1）配置cgi.fix_pathinfo(php.ini)为0并重启php-cgi程序

### 2.HTTP.SYS远程代码执行漏洞（MS15-034）

此漏洞存在于HTTP协议堆栈（HTTP.SYS）中，当HTTP.SYS未正确分析经特殊设计的HTTP请求时会导致此漏洞。成功利用此漏洞的攻击者可以在系统账户的上下文中执行任意代码，可以导致IIS服务器所在机器蓝屏或读取内存中的机密数据。

影响范围：windows7、windows8、windows8.1、Windows server 2008R2、Windows server
2012、Windows server 2012R2

漏洞影响版本：IIS7.5、IIS8.0、IIS8.5

（1）访问IIS7.5默认页面，修改请求添加Range值（Range: bytes=0-18446744073709551615）

若范围416说明存在此漏洞

![1620190177_609223e1522ea1e968c95.png!small](https://image.3001.net/images/20210505/1620190177_609223e1522ea1e968c95.png!small)

![1620190095_6092238fb5fdfe7f97bad.png!small](https://image.3001.net/images/20210505/1620190095_6092238fb5fdfe7f97bad.png!small)

（2）使用msf可以读取目标主机（192.168.64.135）的内存数据

![1620190979_60922703bb7c9e2c91c5e.png!small](https://image.3001.net/images/20210505/1620190979_60922703bb7c9e2c91c5e.png!small)

修复建议

（1）安装修复补丁（KB3042553）

### 3.认证绕过漏洞

Microsoft
IIS中存在认证绕过漏洞和源码泄露漏洞，该漏洞源于对用户提供的输入未经正确的验证。攻击者可利用这些漏洞再服务器进程上下文中获取密码保护资源和查看源代码文件的未授权访问，且有助于进一步攻击。

影响版本：IIS 6.0、IIS 7.5

Microsoft IIS由于无法正确清理用户提供的输入，容易出现身份验证绕过漏洞和源代码泄露漏洞。包含三类绕过：

（1）安装了PHP的Miscrosoft IIS 6.0身份验证绕过：

/admin::$INDEX_ALLOCATION/index.php

（2）Microsoft IIS 7.5经典ASP身份验证绕过（安装配置经典.NET Framework 4.0）：

/admin:$i30:$INDEX_ALLOCATION/index.asp

（3）Microsoft IIS 7.5 .NET源代码公开和身份验证绕过

http://<victimIIS75>/admin:$i30:$INDEX_ALLOCATION/admin.php

复现：

环境windows 7,默认IIS 7.5，

（1）在wwwroot目录下创建admin文件夹，之后通过IIS manger管理器，禁用admin目录的匿名身份验证。

![1620199055_6092468f925a3cca9f5ee.png!small](https://image.3001.net/images/20210505/1620199055_6092468f925a3cca9f5ee.png!small)

![1620199107_609246c347553df145f86.png!small](https://image.3001.net/images/20210505/1620199107_609246c347553df145f86.png!small)

2.访问index.php文件

![1620199167_609246ff5675829da4792.png!small](https://image.3001.net/images/20210505/1620199167_609246ff5675829da4792.png!small)

3.使用“:$i30:$INDEX_ALLOCATION”进行绕过

![1620199263_6092475f1ed41e978e2c4.png!small](https://image.3001.net/images/20210505/1620199263_6092475f1ed41e978e2c4.png!small)

4.文件解析漏洞（IIS7.x解析漏洞条件类似）加身份验证绕过结合，访问index.jpg文件

![1620199350_609247b6d8b8dafc19871.png!small](https://image.3001.net/images/20210505/1620199350_609247b6d8b8dafc19871.png!small)

![1620199591_609248a7865b549bd70c1.png!small](https://image.3001.net/images/20210505/1620199591_609248a7865b549bd70c1.png!small)

修复建议

（1）配置cgi.fix_pathinfo(php.ini)为0并重启php-cgi程序，同时更新最新补丁包

（2）切断方式可以从受认证的目录和.NET Framework版本两方面入手

