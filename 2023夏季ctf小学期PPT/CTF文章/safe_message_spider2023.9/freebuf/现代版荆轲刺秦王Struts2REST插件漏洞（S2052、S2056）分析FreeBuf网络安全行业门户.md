*** 本文作者：进击的大熊2018，本文属FreeBuf原创奖励计划，未经许可禁止转载**

## 0x00 风萧萧兮易水寒，壮士一去兮不复还

战国末期，大秦实力强盛，大有横扫六合之势，在灭了韩、赵两国后，下一个目标就是燕国。

燕国不愿束手就擒，燕太子丹决定派人行刺秦王。

这名勇(bei)敢(cui)的武士，名叫荆轲。

为了能接近秦王，太子丹让荆轲带上两样秦王需要的宝物：秦叛将樊於期的头颅、燕国督亢的地图。而行刺秦王的匕首，就塞在卷着的地图的最里面。

秦王知道燕国已唾手可得，这时燕国又派人来献礼，相当得意，便在咸阳宫接见。

荆轲首先打开装有樊於期头颅的盒子，秦王见状大悦，拍手叫好。

紧接着，镇(jin)定(zhang)的荆轲慢慢打开装有地图的盒子，然后徐徐取出地图，捧给秦王。

在秦王面前，荆轲一点一点展开卷着的地图，展到尽头时，银光一现，露出一把匕首！

荆轲见匕首露现，连忙操起家伙，左手抓住秦王衣袖，右手举起匕首便刺，嘴里还大吼一句三字咒语。。。

然而，秦王保镖可不是省油的灯，后来剧情大反转，荆轲刺秦王不成，为国捐躯了。

![1.png](https://image.3001.net/images/20180416/15238848196305.png!small)  

## **0x01 现代荆轲刺秦**

第二天，秦王稳定情绪之后，赶紧召集安全大会，总结出两要点：

1、安全过滤；匕首居然能进入秦国中央朝堂，应该设置金属过滤装置，这样免于匕首这类凶器能直接威胁秦王。

2、安全保护；秦王一帧一帧慢慢欣赏地图，看到最后竟然是把匕首，幸好身边的保镖不是白养的，及时保护秦王人身安全，记一大功。

最近闹得沸沸扬扬的Struts2 REST插件安全漏洞攻击，跟荆轲刺秦其实是一样的套路：

收集信息：寻找存在漏洞的URL，以便接近攻击主机（打听秦王需要的东西，以便接近秦王）

准备武器：恶意Payload藏在数据包内（凶器匕首藏在地图内）

发起进攻：Payload反序列化后执行恶意代码（图穷匕见）

虽是一样套路，古代荆轲刺秦失败了，但现代的Struts2 REST插件安全漏洞攻击却让人措手不及，究其原因，也是安全过滤、保护机制没能做好。

1、安全过滤：Struts2 REST插件没有对传入的数据进行安全检查，导致恶意数据可以直接传入到XStream里。

2、安全保护；XStream一字一字地解析XML数据并进行反序列化操作，结果竟是恶意代码，而此时并没有保护机制，导致主机被攻击。

## 0x02 模拟攻击

S2-052、056都提到：漏洞发生于Apache
Struts2的REST插件，当使用XStream组件对XML格式的数据包进行反序列化操作，且未对数据内容进行有效验证时，攻击者可通过提交恶意XML数据对应用进行远程攻击。

接下来，根据提到的几个条件，搭建环境，通过模拟攻击的方式体验实际攻击的场景。

整个模拟攻击过程，可能文字看得不是很方便，于是录了个视频，但不知为何一直上传不了，想看的朋友可以在我的微信公众号《进击的大熊》，回复“S2”即可观看演示视频。

1、虚拟机搭建环境

虚拟机安装JDK、Tomcat、Struts2，相关版本信息如下（都可在各自官网下载）：

操作系统 Ubuntu-12.04.5-64位、JDK 1.8-64位、Tomcat 8.5.30、Struts 2.5.12

JDK和Tomcat的安装网上大把教程，注意版本和跟操作系统匹配就行。

Struts 2下载完成后解压，把app目录下的struts2-rest-showcase.war放到tomcat的webapp目录即可。

![2.png](https://image.3001.net/images/20180416/15238848652738.png!small)  

2、启动tomcat，查看IP地址

![3.png](https://image.3001.net/images/20180416/15238848762644.png!small)  

3、使用工具，生成Payload

工具是大神Moritz Bechler写的，源码地址为：<https://github.com/mbechler/marshalsec>，下载下来之后：

a、maven编译 mvn clean package -DskipTests（前提是已安装并配置好Maven）

b、生成Payload（恶意代码是执行"计算机"程序），具体操作：

在生成的target目录，执行：java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.XStream
ImageIO "xcalc" > payload.txt

c、生成的payload.txt即为包含恶意代码的XML数据

至于payload里面的XML数据构造原理，具体可以参照大神Moritz
Bechler写的PDF（<https://github.com/mbechler/marshalsec/blob/master/marshalsec.pdf>）

惭愧，小弟还没能把握住其原理，但用用还是可以的。

![4.png](https://image.3001.net/images/20180416/15238848912353.png!small)  

4、截包篡改数据

浏览器访问 [http://192.168.213.129:8080/struts2-rest-showcase](http://127.0.0.1:8080/struts2-rest-showcase)

打开神器BurpSuite，配置好代理，点击随便一个View，截包。在

http头加上：Content-Type:application/xml ，以及3生成的Payload

![5.png](https://image.3001.net/images/20180416/15238849026879.png!small)  

5、靶机执行恶意代码，弹出计算机

![6.png](https://image.3001.net/images/20180416/15238849142952.png!small)  

6、DOS攻击

为了实现S2-056提到的DOS攻击，写了个python源码，发了N个打开计算机的恶意包，结果导致我那可怜的虚拟机直接奔溃。。。（源码下载链接见文章末尾，仅供学习）

![7.png](https://image.3001.net/images/20180416/15238849265577.png!small)  

## 0x03 跟踪分析

模拟攻击之后，能直观地感受到漏洞的严重性，但是仅如此是不够的。好奇心驱使之下，继续探索造成漏洞的原因。于是，接下来将直接调试源码，从发送恶意代码开始，跟踪整个过程。

 **1、下载并导入源码**

下载得到官方源码包[struts2-rest-showcase-2.5.12.war](https://github.com/yaofeifly/Struts2-052-POC)，并通过eclipse导入到工程中，File—>Import—->war
file

在官网上下载并关联好相关的源码，以便跟踪调试，比如struts2-rest-plugin-2.5.12.jar、xstream-1.4.8.jar、xpp3_min-1.1.4c-sources.jar等

 **2、漏洞来源**

根据漏洞发现者Man Yue
Mo的报告（<https://lgtm.com/blog/apache_struts_CVE-2017-9805>），漏洞来源于ContentTypeHandler接口。

![8.png](https://image.3001.net/images/20180416/15238849513887.png!small)  

**3、突破口设断点**

在源码搜索ContentTypeHandler，有两处发现：

a、XML解释器：在struts-plugin.xml上发现：当content-type为XML时，将指定XStreamHandler，来实现ContentTypeHandler接口。

![9.png](https://image.3001.net/images/20180416/15238849678953.png!small)  

b、在org.apache.struts2.rest.ContentTypeInterceptor上发现关键代码：

ContentTypeHandler handler = selector.getHandlerForRequest(request);

通过request数据获取执行方法，结合上面的发现，应该就是XStreamHandler

在代码下面还可以看到 handler.toObject(reader, target); 对得到的xml数据进行反序列化操作。

为了实现跟踪，于是在这两个地方打断点，并重新调试“模拟攻击”流程。

![10.png](https://image.3001.net/images/20180416/15238855229043.png!small)  

4、用BurpSuite截断发恶意payload之后，程序停在断点处，可以发现此时contentType就是payload设定的application/xml

![11.png](https://image.3001.net/images/20180416/15238849939436.png!small)  

5、紧接着，程序根据得到的contentType值，将handler赋为
XStreamHandler。值得注意的是，这里没有对传入的数据进行任何过滤操作，导致xml数据能传到后续的XStreamHandler

![12.png](https://image.3001.net/images/20180416/1523885254387.png!small)  

6、XStreamHanler.toObject使用了fromXML把XML转化为Java对象，具体通过unmarshal进行反序列化，调试过程发现unmarshal没有对数据进行安全检查，导致恶意代码最终执行

![13.png](https://image.3001.net/images/20180416/15238852828311.png!small)

![14.png](https://image.3001.net/images/20180416/15238852825681.png!small)

![15.png](https://image.3001.net/images/20180416/15238852822668.png!small)

![16.png](https://image.3001.net/images/20180416/15238852833236.png!small)  

## 0x04 防护建议

1、受影响版本

Struts 2.1.1 – Struts 2.5.14.1

2、修复建议

Apache Struts官方已发布2.5.16新版本框架，并在此版本中针对该漏洞进行了安全防护。

建议使用了Apache Struts2 REST插件的用户排查自有框架是否受该漏洞影响，及时升级框架，并替换XML解析器为Jackson
XML处理类JacksonXmlHandler。

P.S. Python-DOS测试源码文件下载：

链接：<https://pan.baidu.com/s/1ZbgHBU3yPZZ--Z3q48qz8Q> 密码：zb4y

 **希望这次的事件，能引起大家对信息安全的重视。**

 **时刻牢记安全无小事，防微杜渐是关键！**

 *** 本文作者：进击的大熊2018，本文属FreeBuf原创奖励计划，未经许可禁止转载**

