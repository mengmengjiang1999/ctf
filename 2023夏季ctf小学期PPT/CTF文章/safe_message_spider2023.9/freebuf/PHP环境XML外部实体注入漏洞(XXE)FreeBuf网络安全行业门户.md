## 1、XML介绍

XML叫做可扩展标记语言，类似于HTML，但是他们之间又有着明显的差别；HTML的主要作用是用来显示数据的，而XML的主要作用是传输和存储数据的。

如果需要在HTML中显示动态数据时，可以将这些数据存储在独立的XML文件中，这样只需要设计HTML来显示和布局，而在修改底层数据时不需要再修改HTML代码。

[《XML语法说明》](https://www.w3school.com.cn/xml/xml_tree.asp)

XML文档结构包括：XML文档声明，DTD文档类型定义，文档元素

libxml是一个XML文档解释器，libxml2.9.0以后，默认不解析外部实体，导致XXE漏洞逐渐消失

## 2、漏洞原理

DTD文档类型定义：用来定义XML文档的结构，它可以在文档内部声明也可以在外部引用

DTD实体：用来定义普通字符或特殊字符的变量，又包括内部实体和外部实体。通过定义实体，可以在文档元素中通过entity-name来引用entity-value的值或者URL返回的值

    
    
    #内部实体定义：<!ENTITY entity-name "entity-value">
    #外部实体定义：<!ENTITY entity-name SYSTEM "URL">
    

XXE漏洞：全称XML外部实体注入漏洞；如果某个漏洞触发点能够上传XML文件，而应用程序解析该XML文件时，没有禁止外部实体的加载，导致攻击者可以通过构造恶意的外部实体造成文件读取、命令执行、内网端口扫描、DOS攻击等

## 3、影响版本

与PHP版本无关

libxml 2.9.0以下

## 4、漏洞复现

进入/vulhub/php/php_xxe，启动靶场：docker-compose up -d

靶场网站根目录中`dom.php`、`SimpleXMLElement.php`、`simplexml_load_string.php`三个文件都存在XXE漏洞，使用burpsuite抓包后通过POST方式上传XML`payload`

    
    
    <?xml version='1.0' encoding='utf-8'?>
    <!DOCTYPE xxe [
    <!ELEMENT name ANY>
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <root>
    <name>&ampxxe</name>
    </root>
    

利用方式一，使用file协议读取本地文件(file协议定义：file://host/path/filename，一般本地文件不需要使用host，所以直接使用：file:///path/filename)

![图片.png](https://image.3001.net/images/20210812/1628772309_611517d5a3c96641f0a3f.png!small)

利用方式二，使用http://URL测试内网主机开放端口，这里直接使用burpsuite的intruder模块测试内网主机192.168.146.135的1-100端口开放情况

将端口设置为变量，然后设置载荷为1-100，开始攻击

![图片.png](https://image.3001.net/images/20210812/1628772295_611517c77f7118f785505.png!small)

通过攻击结果分析，开放了web服务的端口可以比较简单的通过响应的长度来判断，如下面的80-90端口，而像22、3306等端口就不是太好判断了，这些端口需要我们手动的去测试，通过响应时长，响应数据内容长度来判断

![图片.png](https://image.3001.net/images/20210812/1628772331_611517ebbb0c260dd4a70.png!small)

利用方式三：代码执行，需要在特定环境下才能碰到，比如PHP expect模块被加载到了处理XML的应用程序上

利用方式四：对内网服务器进行DOS攻击，由于可以通过该外部实体访问到内网服务器，因此可以通过该漏洞对内网服务器进行DOS攻击。

## 5、漏洞修复

xmllib升级到2.9.0版本之后

处理XML输入的地方禁止外部实体引用

