## **XEE**

XXE -"xml external entity injection"

既"xml外部实体注入漏洞"。

概括一下就是"攻击者通过向服务器注入指定的xml实体内容,从而让服务器按照指定的配置进行执行,导致问题"

也就是说服务端接收和解析了来自用户端的xml数据,而又没有做严格的安全控制,从而导致xml外部实体注入。

##  **XML**

XML用于标记电子文件使其具有结构性的标记语言，可以用来标记数据、定义数据类型，是一种允许用户对自己的标记语言进行定义的源语言。XML文档结构包括XML声明、DTD文档类型定义（可选）、文档元素。

> <!--XML声明-->
>
> <?xml version="1.0"?>
>
> <!--文档类型定义-->
>
> <!DOCTYPE note [ <!--定义此文档是 note 类型的文档-->
>
> <!ELEMENT note (to,from,heading,body)> <!--定义note元素有四个元素-->
>
> <!ELEMENT to (#PCDATA)> <!--定义to元素为”#PCDATA”类型-->
>
> <!ELEMENT from (#PCDATA)> <!--定义from元素为”#PCDATA”类型-->
>
> <!ELEMENT head (#PCDATA)> <!--定义head元素为”#PCDATA”类型-->
>
> <!ELEMENT body (#PCDATA)> <!--定义body元素为”#PCDATA”类型-->
>
> ]]]>
>
> <!--文档元素-->
>
> <note>
>
> <to>Dave</to>
>
> <from>Tom</from>
>
> <head>Reminder</head>
>
> <body>You are a good man</body>
>
> </note>

##  **DTD 的内部声明：**

外部需要一个DTD的文件，比如：note.dtc

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE note [
    
    <!ELEMENT note (to,from,heading,body)>
    
    <!ELEMENT to (#PCDATA)>
    
    <!ELEMENT from (#PCDATA)>
    
    <!ELEMENT heading (#PCDATA)>
    
    <!ELEMENT body (#PCDATA)>
    
    ]>
    
    <note>
    
    <to>Tove</to>
    
    <from>Jani</from>
    
    <heading>Reminder</heading>
    
    <body>Don't forget me this weekend!</body>
    
    </note>

 **DTD的外部声明：**

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    
    <!DOCTYPE ANY [
    
    <!ENTITY content SYSTEM "filename">
    
    ]>
    
    <note>
    
    <to>Tove</to>
    
    <from>Jani</from>
    
    <heading>Reminder</heading>
    
    <body>Don't forget me this weekend!</body>
    
    </note>

##  **漏洞危害：**

1.读取系统文件；

2.执行系统命令；

3.探测内网端口；

4.攻击内部网络。

##  **漏洞防御：**

xxe漏洞存在是因为XML解析器解析了用户发送的不可信数据。然而，要去校验DTD(document type
definition)中SYSTEM标识符定义的数据，并不容易，也不大可能。大部分的XML解析器默认对于XXE攻击是脆弱的。因此，最好的解决办法就是配置XML处理器去使用本地静态的DTD，不允许XML中含有任何自己声明的DTD。通过设置相应的属性值为false，XML外部实体攻击就能够被阻止。因此，可将外部实体、参数实体和内联DTD
都被设置为false，从而避免基于XXE漏洞的攻击。

##  **XXE**

构造一个恶意的payload，通过外部实体引用从而去获取后台服务器的本地文件信息(注：外部引用可以支持http，file，ftp等协议。)

    
    
    <?xml version = "1.0"?>
    
    <!DOCTYPE ANY [
    
    <!ENTITY f SYSTEM "file:///etc/passwd">
    
    ]>
    
    <x>&ampf</x>

![1615451452_6049d53cb4cb30d5d2943.png!small](https://image.3001.net/images/20210311/1615451452_6049d53cb4cb30d5d2943.png!small)

